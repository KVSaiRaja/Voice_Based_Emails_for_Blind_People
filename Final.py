import imaplib
import smtplib
import email
import re
import speech_recognition as sr
import pyttsx3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from gtts import gTTS


def recognize_speech():
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for ambient noise with shorter duration
                speak("Listening...")
                audio = recognizer.listen(source, timeout=5)  # Set a timeout for listening
            text = recognizer.recognize_google(audio, language="en-US", show_all=False)
            return text
        except sr.WaitTimeoutError:
            speak("Listening timeout. Please speak again.")
        except sr.UnknownValueError:
            speak("Could not understand audio. Please repeat your command.")
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
            return None
def listen():
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Adjust for ambient noise with shorter duration
                speak("Listening...")
                audio = recognizer.listen(source, timeout=5)  # Set a timeout for listening
            text = recognizer.recognize_google(audio, language="en-US", show_all=False)
            text_without_spaces = re.sub(r'\s', '', text)
            text_lowercase = text_without_spaces.lower()
            speak(f"you said : {text_lowercase}")
            return text_lowercase
        except sr.WaitTimeoutError:
            speak("Listening timeout. Please speak again.")
        except sr.UnknownValueError:
            speak("Could not understand audio. Please repeat your command.")
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
            return None

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait() 
    
def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload is not None:
                    text = payload.decode()
                    # Remove URLs from the text
                    text_without_urls = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
                    body += text_without_urls
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            payload = msg.get_payload(decode=True)
            if payload is not None:
                text = payload.decode()
                # Remove URLs from the text
                text_without_urls = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
                body = text_without_urls
    return body 
    
def get_gmail_address():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            speak("Listening for email address...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            speak("Recognizing email address...")
            email_address = recognizer.recognize_google(audio)
            email_address = email_address.replace(" ", "").replace("at", "@").replace("8", "@").replace("Gmail", "gmail").replace("male", "mail")  # Replace spaces and convert "at" to '@'
            if "@" not in email_address:
                speak("Sorry, I couldn't recognize the email address. Please try again.")
                continue
            else:
                speak(f"You said email address: {email_address}")
                print(f"You said email address: {email_address}")
                return email_address
        except Exception as e:
            print(e)
            speak("Sorry, I couldn't recognize the email address. Please try again.")
            continue
def get_gmail_password():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening for password...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        speak("Recognizing password...")
        password = recognizer.recognize_google(audio)
        password = password.replace(" ", "").replace("dot", ".").replace("at", "@").replace("hash", "#").replace("dollar", "$").replace("percent", "%").replace("star", "*").replace("ampersand", "&").replace("underscore", "_").replace("exclamation", "!")  # Replace spaces and convert "dot" to '.' and "at" to '@'
        speak(f"You said password: {password}")
        return password
    except Exception as e:
        print(e)
        return ""
def convert_spoken_number_to_int(spoken_number):
    # Define a dictionary to map spoken numbers to their integer equivalents
    number_mapping = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        # Add more mappings as needed
    }
    try:
        # Try to convert the spoken number directly to an integer
        return int(spoken_number)
    except ValueError:
        # If conversion fails, try to map the spoken number to its integer equivalent
        spoken_number_lower = spoken_number.lower()
        return number_mapping.get(spoken_number_lower, None)

def authenticate():
    while True:  # Keep looping until authentication succeeds
        speak("Welcome to the Voice Based Email service for visually impaired people. Please sign in with your Gmail account")
        print("Welcome to the Voice Based Email service for visually impaired people. Please sign in with your Gmail account")

        email=get_gmail_address()
        password=get_gmail_password() # use your google app password ( it will be available at 2fa two factor authentication ) for google security purpose
        #email = input("You said email address: ")
        #password = input("Enter your Gmail password: ")
        try:
            server = imaplib.IMAP4_SSL("imap.gmail.com")
            server.login(email, password)
            speak("Authentication successful!")
            print("Authentication successful!")
            return email,password,server
        except Exception as e:
            speak("Authentication failed:")
            print("Authentication failed:", str(e))
            return None

def ask_to_read_next_mail(i, num_emails_to_read, num_emails, server, folder_type):
    if i < num_emails_to_read - 1:
        speak("Do you want to read the next mail? for 'yes' say y and for 'no' say n: ")
        read_next = recognize_speech()
        if "n" in read_next:
            return False
    elif i == num_emails_to_read - 1 and num_emails == num_emails_to_read:
        speak("All available emails have been read. No further action required.")
        print("All available emails have been read. No further action required.")
        if folder_type == "trash":
            speak("Do you want to permanently delete all emails in the trash folder? for 'yes' say y and for 'no' say n: ")
            delete_emails = recognize_speech()
            if "y" in delete_emails:
                server.select("[Gmail]/Trash")
                server.store("1:*", '+FLAGS', '\\Deleted')
                server.expunge()
                speak("All emails permanently deleted from the trash folder.")
                print("All emails permanently deleted from the trash folder.")
            else:
                speak("No emails were permanently deleted from the trash folder.")
    return True


def process_multiple_emails(num_emails, email_ids, server, num_emails_to_read, folder_type):
    for i in range(num_emails_to_read):
        email_id = email_ids[num_emails - 1 - i]  # Read latest seen mail from upper to lower
        status, response = server.fetch(email_id, '(RFC822)')
        email_data = response[0][1]
        msg = email.message_from_bytes(email_data)
        sender = msg["From"]
        subject = msg["Subject"]
        body = get_email_body(msg)
        speak(f"\nSender: {sender}")
        print(f"\nSender: {sender}")
        speak(f"Subject: {subject}")
        print(f"Subject: {subject}")
        speak(f"Body: {body}")
        print(f"Body: {body}")

        if folder_type == "trash":
            speak("Do you want to send this email back to the inbox? for 'yes' say y and for 'no' say n: ")
            move_email = recognize_speech()
            if "y" in move_email:
                server.store(email_id, '+X-GM-LABELS', '\\Inbox')
                speak("Email sent back to inbox.")
                print("Email sent back to inbox.")
        # Mark the email as unseen
                server.store(email_id, '-FLAGS', '(\\Seen)')
            else:
                speak("Email not sent back to inbox.")
            if not ask_to_read_next_mail(i, num_emails_to_read, num_emails, server, folder_type):
                break
                
        elif folder_type == "spam":
            speak("Do you want to mark this email as not spam and move to Inbox? for 'yes' say y and for 'no' say n: ")
            move_to_inbox = recognize_speech()
            if "y" in move_to_inbox:
                server.store(email_id, '+X-GM-LABELS', '\\Inbox')
                speak("Email marked as not spam and moved to Inbox.")
                print("Email marked as not spam and moved to Inbox.")
            else:
                speak("Do you want to delete this email? for 'yes' say y and for 'no' say n: ")
                delete_mail = recognize_speech()
                if "y" in delete_mail:
                    server.store(email_id, '+X-GM-LABELS', '\\Trash')
                    speak("Email deleted.")
                    print("Email deleted.")
                if not ask_to_read_next_mail(i, num_emails_to_read, num_emails, server, folder_type):
                    break
        elif folder_type == "starred":
            speak("Do you want to move to inbox, delete this mail, or skip? say 'inbox' or 'trash' or 'skip': ")
            command = listen()
            if "inbox" in command:
                server.store(email_id, '+X-GM-LABELS', '\\Inbox')
                speak("Mail moved to inbox")
                print("Mail moved to inbox")
            elif "trash" in command:
                server.store(email_id, '+X-GM-LABELS', '\\Trash')
                speak("Mail moved to Trash.")
                print("Mail moved to Trash.")
            if not ask_to_read_next_mail(i, num_emails_to_read, num_emails, server, folder_type):
                break
                
        elif folder_type == "sent":
            speak("Do you want to delete this mail ? for 'yes' say y and for 'no' say n : ")
            command = recognize_speech()
            if "y" in command:
                server.store(email_id, '+X-GM-LABELS', '\\Trash')
                speak("Mail moved to Trash.")
                print("Mail moved to Trash.")
            if not ask_to_read_next_mail(i, num_emails_to_read, num_emails, server, folder_type):
                    break

def process_emails(server, folder_type):
    status, response = server.search(None, 'ALL')
    email_ids = response[0].split()

    num_emails = len(email_ids)
    speak(f"There are {num_emails} emails in the {folder_type} folder.")
    
    if num_emails == 0:
        speak("No more mails to read")
        return

    if num_emails > 1:  # Additional functionality if there are more than 1 emails
        if folder_type == "trash":
            num_emails_to_read = get_num_emails_to_read(num_emails)
            process_multiple_emails(num_emails, email_ids, server, num_emails_to_read,folder_type)
        
        elif folder_type == "spam":
            num_emails_to_read = get_num_emails_to_read(num_emails)
            process_multiple_emails(num_emails, email_ids, server, num_emails_to_read,folder_type)
            
        elif folder_type == "starred":
            num_emails_to_read = get_num_emails_to_read(num_emails)
            process_multiple_emails(num_emails, email_ids, server, num_emails_to_read,folder_type)

        elif folder_type == "sent":
            num_emails_to_read = get_num_emails_to_read(num_emails)
            process_multiple_emails(num_emails, email_ids, server, num_emails_to_read,folder_type)

    else:  # Existing functionality if there's only 1 email
        for email_id in email_ids:
            status, response = server.fetch(email_id, '(RFC822)')
            email_data = response[0][1]
            msg = email.message_from_bytes(email_data)
            sender = msg["From"]
            subject = msg["Subject"]
            body = get_email_body(msg)
            speak(f"Sender: {sender}")
            print(f"Sender: {sender}")
            speak(f"Subject: {subject}")
            print(f"Subject: {subject}")
            speak(f"Body: {body}")
            print(f"Body: {body}")

            if folder_type == "trash":
                speak("Do you want to send this email back to the inbox? for 'yes' say y and for 'no' say n: ")
                move_email = recognize_speech()
                if "y" in move_email:
                    server.store(email_id, '+X-GM-LABELS', '\\Inbox')
                    speak("Email sent back to inbox.")
                    print("Email sent back to inbox.")
                else:
                    speak("Do you want to permanently delete all emails in the trash folder? for 'yes' say y and for 'no' say n: ")
                    delete_emails = recognize_speech()
                    if "y" in delete_emails:
                        server.select("[Gmail]/Trash")
                        server.store("1:*", '+FLAGS', '\\Deleted')
                        server.expunge()
                        speak("All emails permanently deleted from the trash folder.")
                        print("All emails permanently deleted from the trash folder.")
                    else:
                        speak("No emails were permanently deleted from the trash folder.")

            elif folder_type == "spam":
                speak("Do you want to mark this email as not spam and move to Inbox? for 'yes' say y and for 'no' say n: ")
                move_to_inbox = recognize_speech()
                if "y" in move_to_inbox:
                    # Move the email to Inbox
                    server.store(email_id, '+X-GM-LABELS', '\\Inbox')
                    speak("Email marked as not spam and moved to Inbox.")
                    print("Email marked as not spam and moved to Inbox.")
                else:
                    speak("Do you want to delete this email? for 'yes' say y and for 'no' say n: ")
                    delete_mail = recognize_speech()
                    if "y" in delete_mail:
                        # Delete the email (move to Trash)
                        server.store(email_id, '+X-GM-LABELS', '\\Trash')
                        speak("Email deleted.")
                        print("Email deleted.")

            elif folder_type == "starred":
                speak("Do you want to move to inbox or delete this mail or skip? say 'inbox' or 'trash' or 'skip': ")
                command = listen()
                if "inbox" in command:
                    server.store(email_id, '+X-GM-LABELS', '\\Inbox')
                    speak("Mail moved to inbox.")
                    print("Mail moved to inbox.")
                elif "trash" in command:
                    server.store(email_id, '+X-GM-LABELS', '\\Trash')
                    speak("Mail moved to Trash.")
                    print("Mail moved to Trash.")

            elif folder_type == "sent":
                speak("Do you want to delete this mail ? for 'yes' say y and for 'no' say n : ")
                command = recognize_speech()
                if "y" in command:
                    server.store(email_id, '+X-GM-LABELS', '\\Trash')
                    speak("Mail moved to Trash.")
                    print("Mail moved to Trash.")
                else:
                    speak(" Mail skipped ")
                
def get_num_emails_to_read(num_emails):
    while True:
        try:
            speak(f"How many emails out of {num_emails} would you like to read? ")
            spoken_number = listen()
            num_emails_to_read = convert_spoken_number_to_int(spoken_number)
            if num_emails_to_read <= 0:
                speak("Invalid input. Please enter a number greater than 0.")
                continue
            elif num_emails_to_read > num_emails:
                speak(f"Invalid input. You have {num_emails} emails available. Please enter a number less than or equal to {num_emails}.")
                continue
            else:
                return num_emails_to_read
        except ValueError:
            speak("Invalid input. Please enter a valid integer.")
def compose_email(server, email, password):
    try:
        # Get recipient's email address
        speak("What is the recipient's email address? ")
        recipient = get_gmail_address()
        speak(f"Recipient's email address: {recipient}")
        print(f"Recipient's email address: {recipient}")
        # Get the subject of the email
        speak("What is the subject of the email? ")
        subject = recognize_speech()
        speak(f"Subject: {subject}")
        print(f"Subject: {subject}")
        # Get the body of the email
        speak("What is the body of the email? ")
        body = recognize_speech()
        speak(f"Body: {body}")
        print(f"Body: {body}")

        # Create the email message
        message = MIMEMultipart()
        message['From'] = email
        message['To'] = recipient
        message['Subject'] = subject

        body_text = MIMEText(body, 'plain')
        message.attach(body_text)

        speak("Do you want to add an audio attachment to the email? for 'yes' say y and for 'no' say n ")
        audio_attachment = recognize_speech()
        if "y" in audio_attachment:
            speak("Please speak the content for the audio attachment: ")
            audio_content = recognize_speech()

            # Convert the audio content to a .wav file
            audio_file_path = "audio_attachment.wav"
            tts = gTTS(audio_content, lang='en')
            tts.save(audio_file_path)

            with open(audio_file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {audio_file_path}")

            # Add the attachment to the email
            message.attach(part)
            speak("Audio attachment added successfully!")
            print("Audio attachment added successfully!")

        else:
            speak("No audio attachment requested.")

        text = message.as_string()

        # Send the email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email, password)
        server.sendmail(email, recipient, text)
        server.quit()

        speak("Email sent successfully!")
        print("Email sent successfully!")

    except Exception as e:
        speak("Error sending email:")
        print("Error sending email:", str(e))

def reply_to_email(server, email_address, password, email_id):
    try:
        # Fetch the email
        server.select('inbox')
        status, response = server.fetch(email_id, "(RFC822)")
        if status == 'OK':
            raw_email = response[0][1]
            if isinstance(raw_email, bytes):
                msg = email.message_from_bytes(raw_email)
            else:
                # Decode the string email
                msg = email.message_from_string(raw_email.decode())

            # Get necessary information
            sender = msg["From"]
            subject = msg["Subject"]
            reply_to = msg["Reply-To"] or sender

            # Compose reply
            reply_msg = MIMEMultipart()
            reply_msg["From"] = email_address
            reply_msg["To"] = sender
            reply_msg["Subject"] = f"Re: {subject}"
            speak("Say your reply:")
            reply_text = recognize_speech()
            reply_msg.attach(MIMEText(reply_text, 'plain'))

            # Check if the user wants to add an audio attachment
            speak("Do you want to add an audio attachment to the email? for 'yes' say y and for 'no' say n ")
            audio_attachment = recognize_speech()
            if "y" in audio_attachment:
                speak("Please speak the content for the audio attachment: ")
                audio_content = recognize_speech()

                # Convert the audio content to a .wav file
                audio_file_path = "audio_attachment.wav"
                tts = gTTS(audio_content, lang='en')
                tts.save(audio_file_path)

                with open(audio_file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {audio_file_path}")

                # Add the attachment to the email
                reply_msg.attach(part)
                speak("Audio attachment added successfully!")
                print("Audio attachment added successfully!")

            # Send the reply using SMTP
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.login(email_address, password)
            smtp_server.sendmail(email_address, reply_to, reply_msg.as_string())
            smtp_server.quit()

            speak("Reply sent successfully.")
            print("Reply sent successfully.")
        else:
            speak(f"Error fetching email {email_id}")

    except Exception as e:
        speak("Error replying to email:")
        print("Error replying to email:", str(e))

def access_inbox(server, email, password):
    try:
        # Access the inbox
        server.select("INBOX")

        # Get the count of unseen emails
        status, response = server.search(None, 'UNSEEN')
        unseen_count = len(response[0].split())

        # Get the count of seen emails
        status, response = server.search(None, 'SEEN')
        seen_count = len(response[0].split())
        speak(f"There are {unseen_count} unseen emails and {seen_count} seen emails in the inbox.")
        print(f"There are {unseen_count} unseen emails and {seen_count} seen emails in the inbox.")

        while True:
            speak("\nChoose an option:")
            speak("Read unseen emails")
            speak("Read seen emails")
            speak("Exit")
            speak("say your choice: ")
            choice = listen()

            if "unseen" in choice :
                read_unseen_emails(server, email, password)
            elif "seen" in choice :
                read_seen_emails(server, email, password)
            elif "exit" in choice :
                speak("Exiting.")
                break
            else:
                speak("Invalid choice. Please try again.")

    except Exception as e:
        speak("Error accessing inbox:")
        print("Error accessing inbox:", str(e))

def read_unseen_emails(server, email, password):
    try:
        # Access the inbox
        server.select("INBOX")

        # Get the count of unseen emails
        status, response = server.search(None, 'UNSEEN')
        unseen_count = len(response[0].split())

        if unseen_count == 0:
            speak("No unseen emails in the inbox.")
            return
        elif unseen_count == 1:
            speak("There is one unseen email in the inbox.")
            num_emails_to_read = 1
        else:
            speak("How many unseen emails would you like to read?")
            command = listen()
            num_emails_to_read = convert_spoken_number_to_int(command)

        if num_emails_to_read <= 0:
            speak("Invalid input.")
            return
        status, response = server.search(None, 'UNSEEN')
        email_ids = response[0].split()
        email_ids = email_ids[::-1]  # Reverse order to get the latest emails first

        for index in range(min(num_emails_to_read, len(email_ids))):
            email_id = email_ids[index]
            read_email(server, email, password, email_id)
            if index < num_emails_to_read - 1:
                speak("Do you want to read the next mail? for 'yes' say y and for 'no' say n ")
                command = recognize_speech()
                if "y" not in command:
                    break
    except Exception as e:
        speak("Error reading unseen emails:")
        print("Error reading unseen emails:", str(e))

def read_seen_emails(server, email, password):
    try:
        # Access the inbox
        server.select("INBOX")

        # Get the count of seen emails
        status, response = server.search(None, 'SEEN')
        seen_count = len(response[0].split())

        if seen_count == 0:
            speak("No seen emails in the inbox.")
            return
        elif seen_count == 1:
            speak("There is one seen email in the inbox.")
            num_emails_to_read = 1
        else:
            speak("How many seen emails would you like to read?")
            command = listen()
            num_emails_to_read = convert_spoken_number_to_int(command)

        if num_emails_to_read <= 0:
            speak("Invalid input.")
            return

        status, response = server.search(None, 'SEEN')
        email_ids = response[0].split()
        email_ids = email_ids[::-1]  # Reverse order to get the latest emails first

        for index in range(min(num_emails_to_read, len(email_ids))):
            email_id = email_ids[index]
            read_email(server, email, password, email_id)
            if index < num_emails_to_read - 1:
                speak("Do you want to read the next mail? for 'yes' say y and for 'no' say n")
                command = recognize_speech()
                if "y" not in command:
                    break
    except Exception as e:
        speak("Error reading seen emails:")
        print("Error reading seen emails:", str(e))
def read_email(server, email_address, password, email_id):
    try:
        # Fetch the email
        status, response = server.fetch(email_id, "(RFC822)")
        if status == 'OK':
            raw_email = response[0][1]
            if isinstance(raw_email, bytes):
                msg = email.message_from_bytes(raw_email)
            else:
                # Decode the string email
                msg = email.message_from_string(raw_email.decode())

            # Get necessary information
            sender = msg["From"]
            subject = msg["Subject"]
            body = get_email_body(msg)
            speak(f"Sender: {sender}")
            print(f"Sender: {sender}")
            speak(f"Subject: {subject}")
            print(f"Subject: {subject}")
            speak(f"Body: {body}")
            print(f"Body: {body}")

            # After reading the email, ask the user for further actions
            while True:
                speak("Choose an action for this email Reply or Mark as Spam or Mark as starred or Move to Trash or Skip. Say your choice: ")
                action = listen()
                
                if "reply" in action :
                    reply_to_email(server, email_address, password, email_id)
                    break
                elif "spam" in action :
                    server.store(email_id, '+X-GM-LABELS', '\\Spam')
                    speak("Email marked as spam.")
                    print("Email marked as spam.")
                    break
                elif "star" in action :
                    server.store(email_id, '+X-GM-LABELS', '\\Starred')
                    speak("Email marked as starred.")
                    print("Email marked as starred.")
                    break
                elif "trash" in action :
                    server.store(email_id, '+X-GM-LABELS', '\\Trash')
                    speak("Email moved to trash.")
                    print("Email moved to trash.")
                    break
                elif "skip" in action :
                    speak("No action taken for this email.")
                    break
                else:
                    speak("Invalid choice. Please choose a valid action.")

    except Exception as e:
        speak(f"Error reading email {email_id}:")
        print(f"Error reading email {email_id}:", str(e))

def access_sent_folder(server):
    try:
        server.select('"[Gmail]/Sent Mail"')
        choice = "sent"
        process_emails(server, choice)

    except Exception as e:
        speak("Error accessing Sent Mail folder:")
        print("Error accessing Sent Mail folder:", str(e))

def access_trash_folder(server):
    try:
        # Access the trash folder
        server.select("[Gmail]/Trash")
        choice = "trash"
        process_emails(server, choice)
    except Exception as e:
        speak("Error accessing trash folder:")
        print("Error accessing trash folder:", str(e))

def access_spam_folder(server):
    try:
        # Access the spam folder
        server.select("[Gmail]/Spam")
        choice = "spam"
        process_emails(server, choice)          
    except Exception as e:
        speak("Error accessing spam folder:")
        print("Error accessing spam folder:", str(e))

def access_starred_folder(server):
    try:
        # Access the important folder
        server.select("[Gmail]/Starred")
        choice = "starred"
        process_emails(server, choice)
    except Exception as e:
        speak("Error accessing starred folder:")
        print("Error accessing starred folder:", str(e))
    
def main():
    # Your authentication logic goes here...
    while True:  # Loop until successful authentication
        auth_result = authenticate()
        if auth_result:
            email, password, server = auth_result
            while True:
                speak("You can compose an email, access your inbox, sent folder, starred folder, spam folder, trash folder, or logout. Say your choice.")
                print("You can compose an email, access your inbox, sent folder, starred folder, spam folder, trash folder, or logout. Say your choice.")
                command = listen()  # Get user command via speech

                if "compose" in command:
                    speak("Composing email. Please provide recipient, subject, and body.")
                    compose_email(server, email, password)
                elif "inbox" in command:
                    speak("Accessing inbox.")
                    access_inbox(server, email, password)
                elif "sent" in command:
                    speak("Accessing sent folder.")
                    access_sent_folder(server)
                elif "spam" in command:
                    speak("Accessing spam folder.")
                    access_spam_folder(server)
                elif "trash" in command:
                    speak("Accessing trash folder.")
                    access_trash_folder(server)
                elif "star" in command:
                    speak("Accessing starred folder.")
                    access_starred_folder(server)
                elif "logout" in command:
                    speak("Logging out. Goodbye!")
                    server.logout()  # Logout from the email server
                    break
                else:
                    speak("Invalid command. Please try again.")
            break  # Exit the outer loop when user logs out
        else:
            speak("Failed to authenticate with IMAP server. Please try again.")
            print("Failed to authenticate with IMAP server. Please try again.")

if __name__ == "__main__":
    main()

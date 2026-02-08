import imaplib
import email
from email.header import decode_header
from pdfminer.high_level import extract_text as extract_pdf_text
import tempfile
import os
import chardet

def decodeHeaderField(field):
    if not field:
        return ''
    decodedFragments=decode_header(field)
    decoded=''
    for frag,enc in decodedFragments:
        if isinstance(frag,bytes):
            decoded+=frag.decode(enc or 'utf-8',errors='replace')
        else:
            decoded+=frag
    return decoded

def extractAttachmentsTexts(mailData):
    ret=[]
    for part in mailData.walk():
        contentDisp=part.get('Content-Disposition','')
        if 'attachment' in contentDisp:
            filename=part.get_filename()
            if not filename:
                continue
            decodedFilename,encoding=decode_header(filename)[0]
            if isinstance(decodedFilename,bytes):
                filename=decodedFilename.decode(encoding or 'utf-8',errors='replace')
            payload=part.get_payload(decode=True)
            if not payload:
                continue
            if not isTextRelatedFile(filename):
                continue
            filenameAndText=getFilenameAndText(filename,payload)
            ret.append(filenameAndText)
    return ret

def getFilenameAndText(filename,payload):
    if isPdfFile(filename):
        with tempfile.NamedTemporaryFile(delete=False,suffix='.pdf') as tmp:
            tmp.write(payload)
            tmp.flush()
            text=extract_pdf_text(tmp.name)
        os.unlink(tmp.name)
    else: # shoule be isOtherTextFile(filename)==True
        encodingGuess=chardet.detect(payload)['encoding'] or 'utf-8'
        text=payload.decode(encodingGuess,errors='replace')
    return (filename,text.strip())

def isTextRelatedFile(filename):
    return isPdfFile(filename) or isOtherTextFile(filename)

def isPdfFile(filename):
    return filename.lower().endswith('.pdf')

def isOtherTextFile(filename):
    return filename.lower().endswith( ('.txt','.csv','.log') )

HeaderKeywords=('From:','To:','Date:','Subject:','Cc:','Bcc:')
def extractBody(mailData):
    text=''
    if mailData.is_multipart():
        for part in mailData.walk():
            contentType=part.get_content_type()
            contentDisp=part.get('Content-Disposition','')
            if contentType=='text/plain' and 'attachment' not in contentDisp:
                text=part.get_payload(decode=True).decode(errors='replace')
                break
    else:
        text=mailData.get_payload(decode=True).decode(errors='replace')
    lines=text.strip().splitlines()
    cleanedLines=[]
    headerSection=True
    for line in lines:
        if headerSection and any(line.strip().startswith(k) for k in HeaderKeywords):
            continue
        else:
            headerSection=False
            cleanedLines.append(line)
    return "\n".join(cleanedLines).strip()

kSubject='subject'
kFrom   ='from'
kTo     ='to'
kDate   ='date'
kCc     ='cc'
kBcc    ='bcc'
kBody   ='body'
kAttachments='attachments'
kMailIndex='mailIndex'

def parse_forwardedMail(text):
    """
    parse Fwd:mail text
    """
    lines=text.splitlines()
    headerMap={}
    bodyLines=[]
    foundHeader=False
    for i,line in enumerate(lines):
        striped=line.strip()
        if any(striped.startswith(k) for k in HeaderKeywords):
            foundHeader=True
            key,val=striped.split(':',1)
            headerMap[key.lower()]=val.strip()
        elif foundHeader and striped=='':   # found empty line
            bodyLines=lines[i+1:]
            break
    if not foundHeader:
        return {
            kSubject:'',
            kFrom   :'',
            kTo     :'',
            kDate   :'',
            kCc     :'',
            kBcc    :'',
            kBody   :text.strip(),
        }
    return {
        kSubject:headerMap.get(kSubject,''),
        kFrom   :headerMap.get(kFrom   ,''),
        kTo     :headerMap.get(kTo     ,''),
        kDate   :headerMap.get(kDate   ,''),
        kCc     :headerMap.get(kCc     ,''),
        kBcc    :headerMap.get(kBcc    ,''),
        kBody   :"\n".join(bodyLines).strip(),
    }

def fetchMail(imapServerAddr,imapPort,emailUser,emailPass):
    imap=imaplib.IMAP4_SSL(imapServerAddr,imapPort)
    imap.login(emailUser,emailPass)
    imap.select("INBOX")

    status,messages=imap.search(None,'ALL')
    if status!='OK' or not messages[0]:
        imap.logout()
        return None

    latest=messages[0].split()[-1]
    status,msgData=imap.fetch(latest,'(RFC822)')
    rawEmail=msgData[0][1]
    mailData=email.message_from_bytes(rawEmail)
    imap.logout()
    return mailData

def fetchOldestUnreadMail(imapServer, imapPort, emailUser, emailPass):
    imap=imaplib.IMAP4_SSL(imapServer,imapPort)
    imap.login(emailUser,emailPass)
    imap.select('INBOX')

    status,messages=imap.search(None,'UNSEEN')
    if not messages or not messages[0]:
        imap.logout()
        return None

    mailNums=messages[0].split()
    oldestUnseenMailIndex=mailNums[0]

    status,msgData=imap.fetch(oldestUnseenMailIndex,'(BODY.PEEK[])') 
    if status != 'OK' or not msgData or not msgData[0]:
        imap.logout()
        return None,-1

    rawEmail=msgData[0][1]
    mailData=email.message_from_bytes(rawEmail)

    imap.logout()
    return mailData,oldestUnseenMailIndex

def extractMessage(mailData):
    attachmentsTexts=extractAttachmentsTexts(mailData)
    mailInfoDict={
        kSubject:decodeHeaderField(mailData.get('Subject')),
        kFrom   :decodeHeaderField(mailData.get('From')),
        kTo     :decodeHeaderField(mailData.get('To')),
        kDate   :decodeHeaderField(mailData.get('Date')),
        kCc     :decodeHeaderField(mailData.get('Cc')),
        kBcc    :decodeHeaderField(mailData.get('Bcc')),
        kBody   : '',
        kAttachments:attachmentsTexts
    }
    bodyText=extractBody(mailData)
    mailInfoDict[kBody]=bodyText

    if "fwd:" in mailInfoDict[kSubject].lower():
        forwarded=parse_forwardedMail(mailInfoDict[kBody])
        forwarded[kAttachments]=mailInfoDict[kAttachments]
        mailInfoDict=forwarded
    return mailInfoDict

def genMailContentsPack(mailInfoDict,mailIndex):
    return (mailInfoDict,mailIndex)    

def FetchOldestUnreadMail(imapServerAddr,imapPort,emailUser,emailPass):
    mailData,targetMailIndex=fetchOldestUnreadMail(imapServerAddr,imapPort,emailUser,emailPass)
    if mailData is None:
        return None # no unread mail
    mailInfoDict=extractMessage(mailData)
    return genMailContentsPack(mailInfoDict,targetMailIndex)        


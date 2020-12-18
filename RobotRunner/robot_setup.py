import socket
import tqdm
import os
import logging
import buffer
import sys

import subprocess

try:
    os.mkdir('RobotCode')
except FileExistsError:
    pass

out = subprocess.check_output("pwd").decode("utf8")
path = out[0:len(out)-1] + "/" + "run.py"

process = subprocess.Popen(["python", path], shell=False)

code = True


s = socket.socket()
s.bind(('', 2345))

s.listen(10)
print("Waiting for a connection.....")


while True:

    newCode = True
    file_name = None
    conn, addr = s.accept()
    print("Got a connection from ", addr)
    connbuf = buffer.Buffer(conn)

    while True:
        hash_type = connbuf.get_utf8()
        if not hash_type:
            break
        print('hash type: ', hash_type)

        file_name = connbuf.get_utf8()
        

        if not file_name:
            break


        #file_name = os.path.join('uploads',file_name)
        print('file name: ', file_name)

        file_size = int(connbuf.get_utf8())
        print('file size: ', file_size )

        with open(file_name, 'wb') as f:
            remaining = file_size
            while remaining:
                chunk_size = 4096 if remaining >= 4096 else remaining
                chunk = connbuf.get_bytes(chunk_size)
                if not chunk: break
                f.write(chunk)
                remaining -= len(chunk)
            if remaining:
                print('File incomplete.  Missing',remaining,'bytes.')
            else:
                print('File received successfully.')

    
    if file_name: #If we received a new file
        os.system("rm -R RobotCode/")
        os.mkdir("RobotCode")
        os.system("tar -xf " + file_name)
        os.system("rm " + file_name)
        process.kill()
        process = subprocess.Popen(["python", path], shell=False)


        

    print('Connection closed.')
    conn.close()

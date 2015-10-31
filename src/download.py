import os
import time

def main():
    while True:
        os.system("scp -i ~/.ssh/id_rsa.pub temp@lfd2.banatao.berkeley.edu:~/pic.jpg ../images/pic_out.jpg")
        time.sleep(0.5)

if __name__ == '__main__':
    main()

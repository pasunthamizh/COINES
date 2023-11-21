import unittest
import subprocess
import os

args  = ["file_common.exe", "-w", "file1.txt","12345"]
args1 = ["file_common.exe", "-w", "file2.txt","1245"]
args2 = ["file_common.exe", "-r", "file1.txt","3"]
args3 = ["file_common.exe", "-s", "file1.txt"]


subprocess.run(args)

class TestFileHandling(unittest.TestCase):
    
    # positive test case 
    def test_write_file(self):
        output = subprocess.check_output(args)
        print (output)
        with open('test.txt', 'w') as f:
            f.write('12345')
        with open('test.txt', 'r') as f:
            contents = f.read()
        with open('file1.txt', 'r') as f:
            content1 = f.read()
        self.assertEqual(contents, content1)
        
    # negative test case    
    def test_write_file1(self):
        output = subprocess.check_output(args1)
        print (output)
        with open('test.txt', 'w') as f:
            f.write('12')
        with open('test.txt', 'r') as f:
            contents = f.read()
        with open('file2.txt', 'r') as f:
            content1 = f.read()
        self.assertEqual(contents, content1)

    # positive test case   
    def test_read_file(self):
        output = subprocess.check_output(args2)
        print (output)
        with open('file1.txt', 'r') as f:
           contents = bytes(f.read(3), 'utf-8')
        self.assertEqual(contents, output)
        
    # negative test case    
    def test_read_file(self):
        output = subprocess.check_output(args2)
        print (output)
        with open('file1.txt', 'r') as f:
           contents = bytes(f.read(4), 'utf-8')
        self.assertEqual(contents, output)
        
    # positive test case     
    def test_size_file(self):
        output = subprocess.check_output(args3)
        print (output[13])
        file_size = os.path.getsize('file1.txt')
        print (file_size)
        self.assertEqual(output[13], file_size+48)  

     # negative test case     
    def test_size_file(self):
        output = subprocess.check_output(args3)
        print (output[13])
        file_size = os.path.getsize('file1.txt')
        print (file_size)
        self.assertEqual(output[13], file_size)

if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
import sys, os
import sqlite3


def translate_assist_pre_convert(src):
    isDecoded = False
    try:
        src = src.decode('utf-8')
        isDecoded = True
    except:
        pass
    conn = sqlite3.connect('replace_data.db')
    cursor = conn.cursor()
    cursor.execute("select idx, src, dst from replace_data where mType='jpn' order by idx desc;")
    for row in cursor:
        index = row[0]
        source_word = u'%s' % row[1]
        target_word = u'_assist%s_' % index
        src = src.replace(source_word, target_word)
        #print 'pre convert', index
    cursor.close()
    conn.close()
    if isDecoded:
        src = src.encode('utf-8')
    return src

def translate_assist_recovery(src):
    isDecoded = False
    try:
        src = src.decode('utf-8')
        isDecoded = True
    except:
        pass
    conn = sqlite3.connect('replace_data.db')
    cursor = conn.cursor()
    cursor.execute("select idx, src, dst from replace_data where mType='jpn' order by idx desc;")
    for row in cursor:
        index = row[0]
        source_word = u'_assist%s_' % index
        target_word = u'%s' % row[2]
        src = src.replace(source_word, target_word)
        #print 'revert convert', index
    cursor.close()
    conn.close()
    if isDecoded:
        src = src.encode('utf-8')
    return src

def translate_assist_after(src):
    isDecoded = False
    try:
        src = src.decode('utf-8')
        isDecoded = True
    except:
        pass
    conn = sqlite3.connect('replace_data.db')
    cursor = conn.cursor()
    cursor.execute("select idx, src, dst from replace_data where mType='kor' order by idx desc;")
    for row in cursor:
        index = row[0]
        source_word = u'_assist%s_' % index
        target_word = u'%s' % row[2]
        src = src.replace(source_word, target_word)
        #print 'revert convert', index
    cursor.close()
    conn.close()
    if isDecoded:
        src = src.encode('utf-8')
    return src

def create_database():
    conn = sqlite3.connect('replace_data.db')
    cursor = conn.cursor()
    cursor.execute("create table replace_data (idx, mType, src, dst);")
    conn.commit()
    cursor.close()
    conn.close()

def view_database(target):
    conn = sqlite3.connect('replace_data.db')
    cursor = conn.cursor()
    if target!='all':
        cursor.execute( "select * from replace_data where idx=%s order by idx asc;" % target)
    else:
        cursor.execute( "select * from replace_data where order by idx asc;")
    for row in cursor:
        print row[0], row[1], row[2]
    conn.commit()
    cursor.close()
    conn.close()

def delete_database(idx):
    conn = sqlite3.connect('replace_data.db')
    cursor = conn.cursor()
    cursor.execute( "delete from replace_data where idx=%s;"% idx)
    conn.commit()
    cursor.close()
    conn.close()

def add_database(mType, src, dst):
    src = src.replace("'",'"')
    dst = dst.replace("'",'"')
    if mType=='jpn' or mType=='kor':
        new_index = isAlreadyAdded(src)
        if new_index>0:
            conn = sqlite3.connect('replace_data.db')
            cursor = conn.cursor()
            cursor.execute(
                "insert into replace_data (idx, mType, src, dst) values (%s, '%s', '%s','%s');"% (new_index, mType, src, dst )
            )
            conn.commit()
            cursor.close()
            conn.close()
    else:
        print 'mType error %s' % mType

def isAlreadyAdded(src):
    result = 0
    conn = sqlite3.connect('replace_data.db')
    cursor = conn.cursor()
    cursor.execute("select idx, src, dst from replace_data where src='%s';"% (src))
    lists = cursor.fetchall()
    if len(lists)>0:
        print 'already added word'
        result = 0
    else:
        cursor.close()
        cursor = conn.cursor()
        cursor.execute("select idx, src, dst from replace_data order by idx desc limit 1;")
        lists = cursor.fetchall()
        if len(lists)>0:
            row = lists[0]
            result = row[0] + 1
        else:
            result = 1
    cursor.close()
    conn.close()
    return result


def replace_target_file(filename):
    if filename.find('.txt')>0:
        filename = filename.split('.')[0]
        file = open('%s.txt'% filename, 'r')
        filedata = file.read()
        file.close()
        filedata = filedata.decode('utf-8')
        assisted = translate_assist(filedata)
        file = open('%s.txt'% filename, 'w')
        file.write(assisted.encode('utf-8'))
        file.close()
        print 'file %s converted' % filename 
    #print 'file %s failed' % filename
    
if __name__=='__main__':
    filename = sys.argv[1]
    if filename=='add':
        add_database(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'database added'
    elif filename=='addfile':
        file = open('words.txt','r')
        lists = file.readlines()
        file.close()
        tot = len(lists)
        cnt = 1
        for list in lists:
            list = list.replace('\n','').replace('    ','\t').replace(' ','\t')
            list_arr = list.split('\t')
            print cnt, tot, list
            add_database(list_arr[0], list_arr[1], list_arr[2])
            cnt = cnt + 1
        file = open('words.txt','w')
        file.write('')
        file.close()
        print 'database added %s' % (len(lists))
    elif filename=='create':
        create_database()
    elif filename=='view':
        if sys.argv[2]:
            view_database(sys.argv[2])
        else:
            view_database('all')
    elif filename=='del':
        delete_database(sys.argv[2])
    else:
        if os.path.isdir(filename):
            #is directory
            for a_filename in os.listdir(filename):
                replace_target_file(os.path.join(filename, a_filename))
        else:
            replace_target_file(filename)









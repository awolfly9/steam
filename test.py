#-*- coding: utf-8 -*-

command = '''"`id` INT(8) NOT NULL AUTO_INCREMENT UNIQUE ,"
        "`title` CHAR(25) NOT NULL,"
        "`average` FLOAT NOT NULL,"
        "`rating_people` INT(7) DEFAULT NULL,"
        "`rating_five` CHAR (4) DEFAULT NULL,"
        "`rating_four` CHAR(4) DEFAULT NULL ,"
        "`info_director` CHAR(20) DEFAULT NULL,"
        "`info_screenwriter` CHAR(20) DEFAULT NULL,"
        "`info_starred:` CHAR(20) DEFAULT NULL,"
        "`info_type` CHAR(20) DEFAULT NULL,"
        "`info_region` CHAR(20) DEFAULT NULL,"
        "`info_language` CHAR(20) DEFAULT NULL,"
        "`info_release_date` CHAR(40) DEFAULT NULL,"
        "`info_runtime` CHAR(20) DEFAULT NULL,"
        "`info_other_name` TEXT DEFAULT NULL,"
        "`save_time` TIMESTAMP NOT NULL,"'''


def deal_command(command):
    coms = command.split('\n')
    vars = ''
    vals = ''
    for i, com in enumerate(coms):
        cs = com.split('`')
        vars = vars + cs[1]
        vals = vals + '%s'
        if i < len(coms) - 1:
            vars = vars + ', '
            vals = vals + ', '

    print ('vars:%s' % vars)
    print ('vals:%s' % vals)

    result = 'command = (\"INSERT IGNORE INTO {} \"\n\"(' + vars + ')\"\n"VALUES(' + vals + ')".format())'
    print('result:\n\n%s\n\n\n' % result)

    msg = 'msg=(' + vars + ')'
    print('msg:\n%s\n\n\n' % msg)


if __name__ == '__main__':
    deal_command(command)

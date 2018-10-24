#!/usr/bin/perl
open(fh, "<", "/tmp/creds") or die $!;
my @lines;
while (<fh>)
  {
    chomp $_;
    push (@lines, $_);
  }
close fh or die $!;
open(FH, '>', "/tmp/createdb.sh") or die $!;

print FH "mysql -u root -prootpassword <<MYSQL_SCRIPT\n";
print FH "CREATE DATABASE $lines[1] DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;\n";
print FH "GRANT ALL ON $lines[1].* TO \'$lines[2]\'@\'%\' IDENTIFIED BY \'$lines[3]\';\n";
print FH "FLUSH PRIVILEGES; \n";
print FH "MYSQL_SCRIPT\n";

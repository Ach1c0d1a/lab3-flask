use master
go
-- Create database
create database db_bank 
on  primary (name='db_bank', filename='C:\mssql\data\db_bank.mdf',     size=50Mb, maxsize=150Mb, filegrowth=25Mb)
log on (name='db_bank_log',  filename='C:\mssql\data\db_bank_log.ldf', size=30Mb, maxsize=100Mb, filegrowth=25Mb); 
go

-- Retrieve stored symmetric keys
select * from sys.symmetric_keys
go

-- Create symmetric key (master database)
create master key encryption by password = '23987hxJKL95QYV4369#ghf0%lekjg5k3fd117r$$#1946kcj$n44ncjhdlj'
go

-- Create a certificate
create certificate secure_credit_cards with subject = 'custom credit card number';
go

-- Create symmetric key (current database)
create symmetric key lscck_05
	with algorithm = aes_256
    encryption by certificate secure_credit_cards;


use db_bank

-- Create person table
create table customer(
	cedcustomer varchar(20) not null,
	nombre varchar(30),
	correo varchar(30)
);
go

alter table customer add constraint pk_customer primary key(cedcustomer);
go

-- Create example table
create table cards(
	customer varchar(20) not null,
	creditCard varchar(25) not null,
	encryptedCC varbinary(250) 
);
go
alter table cards add constraint pk_cards primary key(creditCard);
go
alter table cards add constraint fk_cards_customer foreign key(customer) references customer(cedcustomer);
go

-- EncryptByKey(par_1, par_2, par_3, par_4)
--   par_1: key_GUID to be used to encrypt
--   par_2: value to be stored
--   par_3: add authenticator, only if value = 1
--   par_4: authenticator value

-- Open the symmetric key with which to encrypt the data.
open symmetric key lscck_05 decryption by certificate secure_credit_cards;
go

-- Insert data


insert into customer
values('605960578', 'Juanito', 'juani17@gmail.com');
go



insert into cards
values('608960578', '6042210012564010', EncryptByKey(Key_GUID('lscck_05'),'608960578',0));
go


-- Close the key
close symmetric key lscck_04;


-- Retrieve data 
SELECT cd.creditCard
            FROM cards cd
            INNER JOIN customer c ON cd.customer = c.cedcustomer
            WHERE cd.customer = '608960578';





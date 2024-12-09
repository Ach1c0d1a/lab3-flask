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
create symmetric key lscck_04
	with algorithm = aes_256
    encryption by certificate secure_credit_cards;


use db_bank

-- Create person table
create table customer(
	id
	cedcustomer varchar(10) not null,
	nombre varchar(30) not null,
	correo varchar(30) not null
);
go

alter table customer add constraint pk_customer primary key(cedcustomer);
go

-- Create example table
create table cards(
	customer varchar(10) not null,
	creditCard varchar(16) not null,
	encryptedCC varbinary(250) null
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
open symmetric key lscck_04 decryption by certificate secure_credit_cards;
go

-- Insert data


insert into customer
values('605960578', 'Juanito', 'juani17@gmail.com');
go

insert into customer
values('608960578', 'Marian', 'mar15@gmail.com');
go

insert into customer
values('605900698', 'Lucas', 'lu17@gmail.com');
go

insert into cards
values('605960578', '6041710012564010', EncryptByKey(Key_GUID('lscck_04'),'605960578',0));
go

insert into cards
values('608960578', '6042210012564010', EncryptByKey(Key_GUID('lscck_04'),'608960578',0));
go

insert into cards
values('605900698','6041810012569010',EncryptByKey(Key_GUID('lscck_04'),'605900698',1, HashBytes('SHA1',convert(varbinary,500))));
go

insert into card_list
values('605900698','6041810012569020',EncryptByKey(Key_GUID('lscck_04'),'605900698',1, HashBytes('SHA1',convert(varbinary,500))));
go

-- Close the key
close symmetric key lscck_04;


-- Retrieve data 
SELECT cd.creditCard
            FROM cards cd
            INNER JOIN customer c ON cd.customer = c.cedcustomer
            WHERE cd.customer = '608960578';


/*
select c.cedcustomer, c.nombre, cd.creditCard, cd.encryptedCC,
       DecryptByKey(cd.encryptedCC) decryptedCC
from customer c inner join cards cd
on cd.customer = c.cedcustomer;
*/

select cd.creditCard, cd.encryptedCC,
       CONVERT(varchar, DecryptByKey(cd.encryptedCC,1,HashBytes('SHA1',convert(varbinary,500)))) decryptedCC
from customer c inner join cards cd
on cd.customer = c.cedcustomer
where cd.customer = '605900698';

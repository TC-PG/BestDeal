drop table if exists user;
drop table if exists favorites;

create table user(
	id integer not null primary key AUTOINCREMENT ,
	account varchar(200) not null,
	password varchar(200) not null
);

create table favorites(
	id integer not null primary key AUTOINCREMENT ,
	image text not null,
	productName text not null,
	price text not null,
	url text not null,
	user_id integer not null,
	FOREIGN KEY(user_id) REFERENCES user(id)
);



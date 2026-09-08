#users:
#id integer primary key autoincerement
#name text not null
#email text not null
#password text not null (hashed)


#books:
#idbn Text Primary key
#title text not null
#author text not null

#borrowing
#id integer primary key autoincerment
#user_id integer not null
#isbn Text not null
#borroed_at text
#returned_at text
#foreign key (isbn) refrences books(isbn)
#foreign key (user_id) refrences users(id)
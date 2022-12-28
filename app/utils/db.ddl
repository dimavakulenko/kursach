CREATE TABLE IF NOT EXISTS executors (
    id uuid PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    birth_date TEXT not null,
    photo_url TEXT,
    phone_number TEXT,
    country TEXT,
    city TEXT,
    role_id UUID
);
CREATE TABLE IF NOT EXISTS customers (
    id uuid PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL,name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    birth_date TEXT not null,
    photo_url TEXT,
    phone_number TEXT,
    country TEXT,
    city TEXT,
    role_id UUID
);
create table roles(
    id UUID primary key,
    name TEXT NOT NULL);
create table reviews(
    id UUID primary key,
    customer_id UUID NOT NULL,
    executor_id UUID NOT NULL,
    text TEXT,
    rating FLOAT);
create table comments(
    id UUID primary key,
    order_id UUID NOT NULL,
    executor_id UUID NOT NULL,
    confirmed bool);
create table status (
    id UUID primary key,
    name TEXT NOT NULL);
create table deals (
    id UUID primary key,
    comment_id UUID NOT NULL,
    deal_status_executor UUID,
    deal_status_customer UUID,
    files TEXT);
create table order_types(
    id UUID primary key,
    name TEXT,
    description TEXT);
create table orders(
    id UUID primary key,
    customer_id UUID NOT NULL,
    title TEXT,
    description TEXT,
    files TEXT,
    price numeric(10,2),
    type_id UUID NOT NULL,
    date date);
create table basket(
    id UUID primary key,
    completed_order_id UUID NOT NULL,
    customer_id UUID NOT NULL);
alter table reviews add constraint fk_reviews_customer_id foreign key(customer_id) references customers (id);
alter table reviews add constraint fk_reviews_executor_id foreign key(executor_id) references executors (id);
alter table comments add constraint fk_comments_executor_id foreign key(executor_id) references executors (id);
alter table comments add constraint fk_comments_order_id foreign key(order_id) references orders (id);
alter table deals add constraint fk_deals_comment_id foreign key(comment_id) references comments(id);
alter table deals add constraint fk_deals_status_executor_id foreign key(deal_status_executor) references status(id);
alter table deals add constraint fk_deals_status_customer_id foreign key(deal_status_customer) references status(id);
alter table orders add constraint fk_orders_type_id foreign key(type_id) references order_types(id);
alter table basket add constraint fk_basket_customer_id foreign key (customer_id) references customers (id);
alter table basket add constraint fk_basket_order_id foreign key (completed_order_id) references orders (id) ;

alter table executors
    add constraint fk_executor_role_id
    foreign key (role_id)
    REFERENCES roles (id)
ON DELETE CASCADE;
alter table customers
    add constraint fk_customer_role_id
    foreign key (role_id)
    REFERENCES roles (id)
ON DELETE CASCADE;
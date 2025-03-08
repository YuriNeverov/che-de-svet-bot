# Version: 1

create table if not exists users (
  id integer primary key,
  identifier text,
  first_name text not null,
  last_name text
);

create unique index if not exists users_identifier_idx on users (identifier);

create table if not exists operators (
  id integer primary key,
  identifier text,
  rank integer not null
);

create unique index if not exists operators_identifier_idx on operators (identifier);

create table if not exists subscriptions (
  id integer primary key,
  identifier text not null,
  price integer not null,
  description text
);

create table if not exists products (
  id integer primary key,
  subscription_id integer,
  resource_folder_path text not null,
  foreign key (subscription_id) references subscriptions(id)
);

create index if not exists products_subscription_id_idx on products (subscription_id);

create table if not exists product_subscriptions (
  subscription_id integer not null,
  product_id integer not null,
  foreign key (subscription_id) references subscriptions(id),
  foreign key (product_id) references products(id),
  primary key (subscription_id, product_id)
);

create index if not exists product_subscriptions_subscription_id_idx on product_subscriptions (subscription_id);
create index if not exists product_subscriptions_product_id_idx on product_subscriptions (product_id);

create table if not exists product_user_delivered (
  user_id integer not null,
  product_id integer not null,
  foreign key (user_id) references users(id),
  foreign key (product_id) references products(id),
  primary key (user_id, product_id)
);

create index if not exists product_user_delivered_user_id_idx on product_user_delivered (user_id);
create index if not exists product_user_delivered_product_id_idx on product_user_delivered (product_id);

create table if not exists user_subscriptions (
  user_id integer not null,
  subscription_id integer not null,
  start_date datetime,
  end_date datetime,
  foreign key (user_id) references users(id),
  foreign key (subscription_id) references subscriptions(id),
  primary key (user_id, subscription_id)
);

create index if not exists user_subscriptions_user_id_idx on user_subscriptions (user_id);
create index if not exists user_subscriptions_subscription_id_idx on user_subscriptions (subscription_id);

create table if not exists schedules (
  user_id integer not null,
  product_id integer not null,
  delivery_datetime datetime not null,
  elapsed bool not null,
  foreign key (user_id) references users(id),
  foreign key (product_id) references products(id),
  primary key (user_id, product_id)
);

create index if not exists schedules_user_id_idx on schedules (user_id);
create index if not exists schedules_product_id_idx on schedules (product_id);

create table if not exists messages_to_operators (
  id integer primary key,
  user_id integer not null,
  operator_id integer not null,
  msg_text text not null,
  msg_pic_path text,
  sent_datetime datetime not null,
  received_datetime datetime,
  foreign key (user_id) references users(id),
  foreign key (operator_id) references operators(id)
);

create index if not exists messages_to_operators_user_id_idx on messages_to_operators (user_id);
create index if not exists messages_to_operators_operator_id_idx on messages_to_operators (operator_id);
create index if not exists messages_to_operators_sent_datetime_idx on messages_to_operators (sent_datetime);

create table if not exists messages (
  chat_id integer not null,
  id integer not null,
  sender_user_id integer,
  msg_text text,
  msg_resource_path text,
  sent_datetime datetime not null,
  reply_to integer,
  primary key (chat_id, id),
  foreign key (sender_user_id) references users (id),
  foreign key (reply_to) references messages (id)
);

create index if not exists messages_sender_user_id_idx on messages (sender_user_id);
create index if not exists messages_sent_datetime_idx on messages (sent_datetime);
create index if not exists messages_reply_to_idx on messages (reply_to);

create table if not exists user_scenarios (
  user_id integer unique not null,
  scenario_id integer not null,
  state text not null,
  foreign key (user_id) references users (id)
);

create index if not exists user_scenarios_user_id_idx on user_scenarios (user_id);

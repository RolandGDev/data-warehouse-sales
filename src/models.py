from sqlalchemy import Table, Column, Integer, String, MetaData, Numeric, Boolean, ForeignKey, Date

metadata = MetaData()

products = Table('products', metadata,
                 Column('product_id', Integer, primary_key=True),
                 Column('product_name', String(200)),
                 Column('category', String(200)),
                 Column('price', Numeric(10,2)),
                )

dim_product = Table('dim_product', metadata,
                    Column('product_id', Integer, primary_key=True),
                    Column('product_name', String(200)),
                    Column('category', String(200)),
                    Column('price', Numeric(10,2)),
                    )

dim_customer = Table('dim_customer', metadata,
                     Column('customer_id', Integer, primary_key=True),
                     Column('customer_name', String(200)),
                     Column('customer_email', String(200)),
                     Column('city', String(200)),
                     Column('country', String(200)),
                     Column('is_corporate', Boolean)
                     )
dim_date = Table( 'dim_date', metadata,
                  Column('date_id',Integer, primary_key=True),  # Formato YYYYMMDD
                    Column('date', Date, nullable=False, unique=True),
                    Column('day',Integer, nullable=False),
                    Column('month',Integer, nullable=False),
                    Column('quarter',Integer, nullable=False),
                    Column('year',Integer, nullable=False),
                    Column('day_of_week',Integer, nullable=False),
                    Column('is_weekend',Boolean, default=False),
                    Column('is_holiday',Boolean, default=False)
                                 )

fact_sales = Table('fact_sales', metadata,
                   #chave_primaria
                   Column('sale_id', Integer, primary_key=True),

                   #chaves_estrangeiras(FKS)
                   Column('date_id', Integer,ForeignKey('dim_date.date_id'), nullable=False),
                   Column('customer_id', Integer, ForeignKey('dim_customer.customer_id'), nullable=False),
                   Column('product_id', Integer, ForeignKey('dim_product.product_id'), nullable=False),

                   #METRICAS(FATOS)
                   Column('quantity', Integer, nullable=False),
                   Column('unit_price', Numeric(10,2),nullable=False),
                   Column('total_amount', Numeric(10,2),nullable=False)
                   )

def create_tables(engine):
    metadata.create_all(engine)
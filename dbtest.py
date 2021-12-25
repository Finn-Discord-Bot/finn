from connect_database import *

# add_stock(userid, ticker, qnty, date)
add_stock(215212898778218496, "HOOD", 1.12345, '2021-12-01')
add_stock(215212898778218496, "AAPL", 345, '2021-12-01')
add_stock(215212898778218496, "TSLA", 1, '2021-12-01')
add_stock(215212898778218496, "V", 123, '2021-12-01')
add_stock(215212898778218496, "BBY", 90.1345, '2021-12-01')
add_stock(215212898778218496, "GME", 12, '2021-12-01')

print(get_portfolio(215212898778218496))
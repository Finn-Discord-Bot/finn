from connect_database import *
# add_stock(userid, ticker, qnty, date)
add_stock(215212898778218496, "HOOD", 1.12345, '2020-12-04')
add_stock(215212898778218496, "AAPL", 345, '2021-2-21')
add_stock(215212898778218496, "TSLA", 1, '2021-12-01')
add_stock(215212898778218496, "V", 123, '2021-12-11')
add_stock(215212898778218496, "BBY", 90.1345, '2020-12-01')
add_stock(215212898778218496, "GME", 12, '2021-11-01')

print(get_portfolio(215212898778218496))   
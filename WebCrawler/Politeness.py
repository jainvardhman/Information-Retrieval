__author__ = 'Vardhman'

import datetime
from datetime import  datetime
from time import time
from datetime import  timedelta
hashDomainLastCalled = {}
SECOND_ONE = 1000000

# this is used to keep track of what domain was called at what time
# and while crawling any domain we need to check in this hash if
# the time elapsed is greater than one second or not
# here we should use the md5 encoding technically, wont do it right now
# as it would be code duplication, will write timing logic here

# here we are taking start time which would be time stamp when a doman is called
# end time would actually be the time stamp when the domain is being called again
# if it is the list. thne we have to compute new_time which is start time +1 second
# if the new time is greater than that time then we can crawl that page again


start_time = datetime.now()
for i in range(1,10000000):
    cnt =cnt +1
end_time = datetime.now()
new_time = start_time + timedelta(seconds=1)

print(start_time)
print(end_time)
print(new_time)

if end_time > new_time:
    print ("go ahead")
else:
    print("stop")

# MSTP

MSTP (Min-Send Transfer Protocol) is an application layer protocol that aims at transferring information between the server-side and the client-side of Min-send.

The general format of MSTP messages is as follows:

~~~text
<TYPE> <ACTION> 
<HEADERS>

<DATA>
~~~

MSTP messages encompass three distinct types: request (REQ), response (RES), and acknowledgement (ACK). Both the server-side and client-side can initiate the transmission of these message types. A request message is dispatched to await a corresponding response, while an acknowledgement message serves as a unilateral communication method to convey information to the recipient.

The action serves as a string that specifies the purpose of a request or an acknowledgement message. Depending on this action string, the server-side or the client side will execute distinct operations.

Headers, integral to each message, consist of key-value pairs representing additional data. Each pair is linked by an equal sign (=). The keys are comprised of English characters, numbers, and hyphens. The leftmost equal sign serves as the delimiter between the key and the associated value.

~~~text
time=1703847211
type=file
file-name=test.txt
~~~
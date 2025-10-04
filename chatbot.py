from database import Item, all_orders, user_orders
import time

# limit for invalid inputs
STRIKE_LIMIT = 2

# Key words to allow user flexibility
HELP = "help"
EXIT = ["quit", "exit"]
YES = ["yes", "ya", "yea", "yeah", "y", "ok", "sure"]
NO = ["no", "na", "nah", "n", "idk", "nope"]

# This is an external link. Click at your own risk... 
shopping_link = "amazon.com"
# shopping_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

class AskHelp(Exception):
    """Exception class used to signal the user needs help. """
    pass


def greeting(name:str="Juji") -> None:
    """
    Greet the user, and introduce the chatbot assistant.

    Args:
        name (str): The Assistant's name
    """
    print("\n*********************************************************************\n")
    print(f"Hello! My name is {name}.  I'm here to help you find your package ... \n\n")
    print(f"To call for help at anytime, type 'help'.\nTo leave this chat at anytime, type 'exit' or 'quit'.\n")
    print("*********************************************************************\n")
    print(f"\n\n")


def prompt_user(prompt:str = "") -> str | AskHelp:
    """
    Prompt the user for input, and cleans the response.  
    Raises `AskHelp` if the user enters "help".
    Exits the program if the user types "quit" or "exit". 

    Args:
        prompt (str): The message to show to the user.

    Returns:
        str: The cleaned (stripped and lowercased) user input.
    """
    response = input(prompt)
    response = response.lower().strip()

    # Call for help or exit the program.
    if response in HELP:
        raise AskHelp

    if response in EXIT:
        exit_chat()

    return response


def __get_user_info() -> Item | None:
    """
    Collects the user's email and attempts to locate their orders.
    If multiple orders exist, prompt the user for the product seller and/or name for further filtering.

    Returns:
        Item | list[Item]: Matching order(s) if found.
    
    Raises:
        `AskHelp`: If the input is invalid, or there are no matching orders.
    """

    # get the user email
    def get_email():
        """
        Prompts the user for a valid gmail address.

        Returns:
            str: User's valid email address.

        Raises:
            `AskHelp` if the user enters an invalid email address `STRIKE_LIMIT` or more times.

        """
        strike = 0
        email = prompt_user(f"What email address did you use to make this order? ")
        print(f"\n")
        
        # While the email is invalid, and we still have tries left
        while strike < STRIKE_LIMIT and email[-10:] != "@gmail.com":
            email = prompt_user(f"Please enter a valid email address:  ")
            strike += 1
     
        # return a valid email
        if email[-10:] == "@gmail.com":
            return email
        
        # no strikes left; ask for help
        print("Too many invalid attempts....\n")
        raise AskHelp

        
    user_email = get_email()
    print(f"\n")
    # Email doesn't exist
    if user_email not in user_orders:
        print(f"Hmmm... we can't seem to find this email in our database.\n")
        raise AskHelp

    orders = user_orders.get(user_email, None)

    # Email exists, no orders associated
    if len(orders) == 0:
        print(f"Hmmm... we can't seem to find any orders under this email address.\n")
        raise AskHelp
    
    # Found one order
    elif len(orders) == 1:
        print(f"Great! We found your package!")
        display_orders(orders)
        return orders
    
    else:
        # Found multiple orders.  Filter by either seller or product name.
        choice = prompt_user(f"You have {len(orders)} orders under this email address.  Would you like to search by <seller> or <product name>?  ")
        print(f"\n")
        if ("seller" in choice or "brand" in choice or "store" in choice):
            order = find_product("seller", "product_name", orders)
        elif ("name" in choice or "product" in choice):
            order = find_product("product_name", "seller", orders)
        else:
            raise AskHelp

        # Provide the user with transparency
        assert isinstance(order, list)
        if len(order) == 1:
            print(f"Great News! We found your package!\n")
        else:
            print(f"We found {len(order)} orders matching your criteria.\n")
        display_orders(order)

        return order
         

def find_product(lookup_method1:str, lookup_method2:str=None, options:list[Item]=None, strike:int=0) -> list[Item]:
    """
    Prompts the user for input values based on the lookup method.
    Then, search a list of orders by `lookup_method1`. If multiple matches remain, retry
    with `lookup_method2` to narrow results.

    Args:
        lookup_method1 (str): Primary attribute to search.
        lookup_method2 (str, optional): Secondary attribute if the first search yields multiple orders.
        options (list[Item]): Orders to filter.
        strike (int): Retry count for narrowing.

    Returns:
        list[Item]: Matching orders (ideally one).

    Raises:
        AskHelp: If no matches are found.
    """

    param1= prompt_user(f"What's the {lookup_method1}? ")
    print(f"\n")

    filtered_orders = [order for order in options if getattr(order, lookup_method1, None) == param1]
        
    # No order exists
    if len(filtered_orders) == 0:
        print(f"Hmmm... we can't seem to find any orders under this {lookup_method1}.\n")
        raise AskHelp

    # Order is Found
    if len(filtered_orders) == 1:
        return filtered_orders

    # Multiple orders exists 
    print(f"We found {len(filtered_orders)} products under this {lookup_method1}\n")
    if strike == 0 and lookup_method2:
        # Retry filtering with secondary attribute
        return find_product(lookup_method2, None, filtered_orders, (strike+1))
    
    # This is the second search, and we still have multiple matches; return them all
    return filtered_orders
    

def get_order() -> Item | str | None:
    """
    Attempts to locate the user's order first by tracking number, then by email + order info.

    Returns:
        List[Item] | None: Matching order(s), or None if the order does not exist.

    Raises:
        AskHelp: If input(s) are invalid or help is requested.
    """

    query = prompt_user(f"Please enter your tracking number (Type 'no' if you forgot): ")
    print(f"\n")
    if query in NO or "no" in query:
        print(f"No problem! Let's try to locate it by email. \n")
        return __get_user_info()
    
    try:
        tracking_num = int(query)
        order = all_orders.get(tracking_num, None)
        
        # The tracking number exists
        if order:
            print(f"Great news! We found your order!\n")
            display_orders([order])
            return [order]
        
        # Try searching by email + order info
        choice = prompt_user(
            "Sorry. I cannot find your order in our system. Would you like to try locating it by email?\n"
            "(Enter 'yes' or 'no'):  "
        )
        print(f"\n")
            
        if "yes" in choice or choice in YES:
            return __get_user_info()
    
        elif "no" in choice or choice in NO:
            return None
        else:
            raise AskHelp
    
    except Exception as _:
        print(f"Unknown selection.\n")
        raise AskHelp
  

def display_orders(orders:list[Item]) -> None:
    """
    Prints the details about one or more orders.  

    Args:
        orders (list[Item]): The list of orders to display.
    """

    if orders:
        if isinstance(orders, Item):
            orders = [orders]
        print(f"======================== Here Are Your Orders ==============================")
        for i, order in enumerate(orders):
            print(f"\n")
            print(f"Order {i}:\n")
            print(f"  Order ID: {order.id}")
            print(f"  Name:     {order.product_name}")
            print(f"  Seller:   {order.seller}")
            print(f"  Status:   {order.status}")
            print(f"\n")
        print(f"\n")


def cancel_order(order:Item) -> None:
    """
    Cancel the user's order and remove it from the database.

    Args:
        order (Item): The user's order to cancel
    """   
    if isinstance(order, list):
        assert len(order) == 1
        order = order[0]    
    
    # Remove it from the user database and the tracking number database
    user_email = order.user_email
    user_orders[user_email].remove(order)
    del all_orders[order.id]

    # Tell the user
    print(f"==========================================================================\n")
    print(f"Your order has been successfully cancelled!\n")
    print(f"  Order ID:  {order.id}")
    print(f"  Item Description:   {order.product_name} (sold by {order.seller})\n\n\n")
    print(f"A refund will be issued within 5 business days. Thank you for your patience!\n")
    print(f"===========================================================================\n\n")



def call_help() -> None:
    """
    Simulate contacting customer service
    """
    user_choice = prompt_user("Would you like to call for help?  ")
    if user_choice in YES or "yes" in user_choice:
        print(f"\n\n")
        print(f"===========================================================================")
        print(f"Dialing customer service.  Please wait on the line... ")
        time.sleep(2)
        print("\n\n...\n\n")
        time.sleep(2)
        print(f"Thank you for calling customer support. We hope we were able to assist you.")
        print(f"===========================================================================")

        print("\n\n")
        time.sleep(1) 
    
    
def exit_chat() -> None:
    """
    Exit the chat gracefully.
    """
    print("\n\n\n\n")
    print("***************************************************************************")
    print(f" Thanks for chatting with me.  Have a nice day! :) ")
    print("***************************************************************************\n")
    exit()



def offer_actions(order:list[Item] = None) -> Item | list[Item] | None:
    """
    Offers and carries out the next-step actions to the user, depending on whether an order was found.

    Args:
        order (list[Item] | None): The list of current orders context (preferably one).

    Returns:
        Item | list[Item] | None: The updated order context.
    
    Raises:
        AskHelp: If the user enters an invalid input or asks for it.
    """
    
    print("---------------------------------------------------------------------------\n")
    # The package is not found
    if order is None:
        query = prompt_user(
            "What do you want to do next? \n\n"
            "  <1> Speak with a live agent\n"
            "  <2> Order something else\n"
            "  <3> Track another package\n\n"
            "(Enter a number):  "
        )
        print(f"\n")
        try: 
            query = int(query)
            if query == 1:
                raise AskHelp
            elif query == 2:
                print(f"I've sent a link below.  Happy shopping!\nShopping Link:  {shopping_link}")
                exit_chat()
            elif query == 3:
                return get_order()
            else:
                print(f"Sorry, I can only assist you with those 3 options :( \n")
                raise AskHelp

        except ValueError as _:
            print(f"I'm sorry. I cannot understand your input. \n")
            raise AskHelp
    
    # The package is found
    else:
        query = prompt_user(
            "What do you want to do next? \n\n"
            "  <1> View order\n"
            "  <2> Track another package\n"
            "  <3> Cancel your order\n"
            "  <4> Speak with a live agent\n\n"
            "(Enter a number):  "
        )
        print(f"\n")
        try:
            query = int(query)
            if query == 1:
                display_orders(order)
                return order
            if query == 2:
                return get_order()
            elif query == 3:
                cancel_order(order)
                return None
            elif query == 4:
                raise AskHelp
            else:
                print(f"Sorry, I can only assist you with those 4 options :( \n")
                raise AskHelp
       
        except ValueError as e:
            print(f"I'm sorry. I cannot understand your input. \n")
            raise AskHelp


def main():
    greeting()
    try:
        order = get_order()
    except AskHelp:
        call_help()
        order = None
    
    while True:
        try:
            order = offer_actions(order)
        except AskHelp:
            call_help()
            continue


if __name__ == "__main__":
    main()

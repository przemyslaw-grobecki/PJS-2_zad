from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Any, Dict, Iterator, List, Optional, Text
from fuzzywuzzy import fuzz
import json
import datetime

#Load config
menuFile = open("../rasa_chat_bot/actions/menu.json", 'r')
menu = json.load(menuFile)
opening_hours_file = open("../rasa_chat_bot/actions/opening_hours.json", 'r')
opening_hours = json.load(opening_hours_file)
current_receipt = []

def CheckIfOpen() -> bool:
    current_time = datetime.datetime.now()
    today = list(opening_hours["items"].keys())[current_time.weekday()]
    return current_time.hour > opening_hours["items"][today]["open"] and current_time.hour < opening_hours["items"][today]["close"] #To test comment this out and replace with True

class ActionOrderDish(Action):
    def name(self) -> Text:
        return "action_order_dish"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not CheckIfOpen():
            dispatcher.utter_message(text="Sorry, currently we are closed. Our Opening hours are: {}".format(opening_hours))
            return []
        
        order_decorated = tracker.get_slot("order_decorated")
        order = tracker.get_slot("order")
        output_message = []
        
        if (not order) and (not order_decorated):
            dispatcher.utter_message(text="I did not find one of your order dishes in our menu. Please, try ordering again.")
            return []
        
        dish_found = False
        if order:
            for item in order:
                for dish in menu["items"]:
                    if(fuzz.ratio(dish["name"].lower(), item.lower()) > 85):
                        current_receipt.append(dish)
                        dish_found = True     
            output_message.extend(order)
            
        if order_decorated:
            for item in order_decorated:
                for dish in menu["items"]:
                    if(fuzz.partial_ratio(dish["name"].lower(), item.lower()) > 85):
                        dish_decorated = {
                            **dish,
                            "notes": item 
                        }
                        current_receipt.append(dish_decorated) 
                        dish_found = True        
            output_message.extend(order_decorated)
        
        if not dish_found:
            dispatcher.utter_message(text="I did not find one of your order dishes in our menu. Please, try ordering again.")
            return [SlotSet("order", []), SlotSet("order_decorated",[])]

        if len(output_message) == 0 :
            dispatcher.utter_message(text="I did not find one of your order dishes in our menu. Please, try ordering again.")
            return [SlotSet("order", []), SlotSet("order_decorated",[])]

        dispatcher.utter_message(text="I have added {} to your receipt sir/mam. Anything else?".format(output_message))
        return [SlotSet("order", []), SlotSet("order_decorated",[])]


class ActionListMenu(Action):
    def name(self) -> Text:
        return "action_list_menu"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not CheckIfOpen():
            dispatcher.utter_message(text="Sorry, currently we are closed. Our Opening hours are: {....}")
            return []
            
        dispatcher.utter_message(text="In our menu we have got:\n")
        for menuItem in menu["items"]:
            dispatcher.utter_message(text="{} for the price of {} which can be ready in {}".format(menuItem["name"],menuItem["price"],menuItem["preparation_time"]))
    
        dispatcher.utter_message(text="Can I take Your order now?")
        return []

class ActionConfirmOrder(Action):
    def name(self) -> Text:
        return "action_confirm_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        total_names = []
        for dish in current_receipt:
            total_names.append(dish["name"])
        dispatcher.utter_message(text="Can we confirm that this is everything you ordered? {}".format(current_receipt))
        return []

class ActionSumUpTheOrder(Action):
    def name(self) -> Text:
        return "action_sum_up_order"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        total_time = 0
        total_spend = 0
        for dish in current_receipt:
            total_spend+=dish["price"]
            total_time+=dish["preparation_time"]

        dispatcher.utter_message(text="Thank You for ordering in our restaurant. We inform You that your shipment will be ready for transport in {} minutes. The total cost is {}$. Have a nice meal :-)".format(total_time*60, total_spend))
        current_receipt.clear()
        return []

class ActionProvideOpeningHours(Action):
    def name(self) -> Text:
        return "action_provide_opening_hours"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Please have a look at our opening hours board:\n {}".format(opening_hours))
        return []
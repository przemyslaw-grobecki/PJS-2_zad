from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Any, Dict, Iterator, List, Optional, Text
from fuzzywuzzy import fuzz
import json

#Load config
#menu = {}
#with open("menu.json") as menuFile:
#    menu = json.load(menuFile)
#
#openingHours = {}
#with open("opening_hours.json") as openingHoursFile:
#    openingHours = json.load(openingHoursFile)

#order = []

menu = {
    "items": [
      {
        "name": "Lasagne",
        "price": 16,
        "preparation_time": 1
      },
      {
        "name": "Pizza",
        "price": 12,
        "preparation_time": 0.5
      },
      {
        "name": "Hot-dog",
        "price": 4,
        "preparation_time": 0.1
      },
      {
        "name": "Burger",
        "price": 12.5,
        "preparation_time": 0.2
      },
      {
        "name": "Spaghetti Carbonara",
        "price": 15,
        "preparation_time": 0.5
      },
      {
        "name": "Tiramisu",
        "price": 11,
        "preparation_time": 0.15
      }
    ]
  }

opening_hours = {
    "items": 
       {
         "Monday": {"open":8,"close":20 },
         "Tuesday": {"open":8,"close":20 },
         "Wednesday": {"open":10,"close":16 },
         "Thursday": {"open":8,"close":20 },
         "Friday": {"open":8,"close":20 },
         "Saturday": {"open":10,"close":16 },
         "Sunday": {"open":0,"close":0 }
       }  
   }
   
current_receipt = []

def CheckIfOpen() -> bool:
    return True

def CheckIfInMenu() -> bool:
    return True

class ActionOrderDish(Action):
    def name(self) -> Text:
        return "action_order_dish"
    def run(self,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not CheckIfOpen():
            dispatcher.utter_message(text="Sorry, currently we are closed. Our Opening hours are: {....}")
            return []
        if not CheckIfInMenu(): 
            dispatcher.utter_message(text="I did not find one of your order dishes in our menu. Please, try ordering again.")
            return []
        order_decorated = tracker.get_slot("order_decorated")
        order = tracker.get_slot("order")
        output_message = []
        
        if (not order) and (not order_decorated):
            dispatcher.utter_message(text="I did not find one of your order dishes in our menu. Please, try ordering again.")
            return []
        
        if order:
            for item in order:
                for dish in menu["items"]:
                    if(fuzz.ratio(dish["name"].lower(), item.lower()) > 85):
                        current_receipt.append(dish)     
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
            output_message.extend(order_decorated)
        
        
        dispatcher.utter_message(text="I have added {} to your receipt sir/mam. Anything else?".format(output_message))
        return []


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

        dispatcher.utter_message(text="Thank You for ordering in our restaurant. We inform You that your shiment will be ready for transport in {} minutes. The total cost is {}$. Have a nice meal :-)".format(total_time*60, total_spend))
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
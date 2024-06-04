#Student name = Sivkim Chhem
#Student_ID = s4071552


import os
import datetime

#creat class Customer
class Customer:
    def __init__(self, ID, name, reward):
        self.ID = ID
        self.name = name
        self.reward = reward

    def get_reward(self, final_cost):
        return final_cost

    def get_discount(self):
        pass

    def update_reward(self, reward):
        self.reward += reward 

    def display_info(self):
        pass

#create class BasicCustomer
class BasicCustomer(Customer):
    reward_rate = 1.0

    def __init__(self, ID, name, reward, reward_rate=None):
        super().__init__(ID, name, reward)
        self.reward_rate = reward_rate if reward_rate is not None else self.reward_rate

    def get_reward(self, total_cost):
        return round(self.reward_rate * total_cost)

    def update_reward(self, value):
        self.reward += value  

    def display_info(self):
        print(f"Customer ID: {self.ID}, Name: {self.name}, Reward: {self.reward}, Reward Rate: {self.reward_rate}")

    @classmethod
    def set_reward_rate(cls, rate):
        cls.reward_rate = rate

#create class VIPCustomer
class VIPCustomer(BasicCustomer):
    discount_rate = 0.08

    def __init__(self, ID, name, reward, reward_rate, discount_rate=None):
        super().__init__(ID, name, reward, reward_rate)
        self.discount_rate = discount_rate if discount_rate is not None else self.discount_rate

    def get_discount(self, total_cost):
        return total_cost * self.discount_rate

    def get_reward(self, final_cost):
        return super().get_reward(final_cost)

    def display_info(self):
        print(f"Customer ID: {self.ID}, Name: {self.name}, Reward: {self.reward}, Reward Rate: {self.reward_rate}, Discount Rate: {self.discount_rate}")

    @classmethod
    def set_reward_rate(cls, rate):
        cls.reward_rate = rate

    def set_discount_rate(self, rate):
        self.discount_rate = rate

#create class Product
class Product:
    def __init__(self, ID, name, price, prescription_required):
        self.ID = ID
        self.name = name
        self.price = round(price, 2)  
        self.prescription_required = prescription_required == 'y'

    def display_info(self):
        prescription_text = 'y' if self.prescription_required else 'n'
        print(f"Product ID: {self.ID}, Name: {self.name}, Price: {self.price:.2f}, {prescription_text}")

#create class Bundle
class Bundle:
    def __init__(self, ID, name, products):
        bundle_price = 0.80
        self.ID = ID
        self.name = name
        self.products = products
        self.price = round(sum(product.price for product in products) * bundle_price, 2)
        self.prescription_required = any(product.prescription_required for product in products)

    def display_info(self):
        product_details = ', '.join(prod.name for prod in self.products)
        prescription_text = 'y' if self.prescription_required else 'n'
        print(f"Bundle ID: {self.ID}, Name: {self.name}, Products: [{product_details}], Price: {self.price:.2f}, {prescription_text}")

#create class Order
class Order:
    def __init__(self, customer, product_quantities, total_cost, earned_rewards, timestamp):
        self.customer = customer
        self.product_quantities = product_quantities  
        self.total_cost = total_cost
        self.earned_rewards = earned_rewards
        self.timestamp = timestamp

    def compute_cost(self):
        total_cost_before_discount = sum(product.price * quantity for product, quantity in self.product_quantities)
        discount = 0

        if isinstance(self.customer, VIPCustomer):
            discount = self.customer.get_discount(total_cost_before_discount)

        final_cost = total_cost_before_discount - discount
        reward = self.customer.get_reward(final_cost)

        return round(total_cost_before_discount, 2), round(discount, 2), round(final_cost, 2), round(reward, 2)

    def deduct_rewards(self, final_cost):
        if self.customer.reward >= 100:
            discount = (self.customer.reward // 100) * 10
            if discount >= final_cost:
                discount = final_cost
            self.customer.reward -= (discount // 10) * 100
            final_cost -= discount
        else:
            if self.customer.reward > 0:
                if self.customer.reward >= final_cost:
                    self.customer.reward -= final_cost
                    final_cost = 0
                else:
                    final_cost -= self.customer.reward
                    self.customer.reward = 0
        return final_cost

    def process_order(self):
        total_cost_before_discount, discount, final_cost, reward = self.compute_cost()
        final_cost = self.deduct_rewards(final_cost)
        
        self.total_cost = final_cost
        self.earned_rewards = reward

        self.customer.update_reward(reward)
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#create class Record
class Record:
    def __init__(self):
        self.customers = []
        self.products = []
        self.orders = []

    def read_customers(self, filename):
        try:
            with open(filename, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    parts = line.strip().split(',')
                    if len(parts) < 3:
                        print(f"Invalid format in line {line_num}: {line.strip()}")
                        continue
                    cust_id = parts[0].strip()
                    name = parts[1].strip().lower()
                    try:
                        reward_rate = int(parts[2])
                    except ValueError as e:
                        print(f"Error parsing reward in line {line_num}: {line.strip()} -> {e}")
                        continue
                    if cust_id.startswith('B'):
                        reward = int(parts[3])
                        customer = BasicCustomer(cust_id, name, reward, reward_rate)
                    elif cust_id.startswith('V'):
                        reward = int(parts[4])
                        discount_rate = float(parts[3])
                        customer = VIPCustomer(cust_id, name, reward, reward_rate, discount_rate)
                    else:
                        print(f"Invalid customer ID format in line {line_num}: {line.strip()}")
                        continue
                    self.customers.append(customer)
        except FileNotFoundError:
            print(f"File not found: {filename}")
            return False
        except Exception as e:
            print(f"An error occurred while reading the file: {filename} -> {e}")
            return False
        return True

    def read_products(self, file_name):
        try:
            with open(file_name, 'r') as file:
                product_lines = file.readlines()

            individual_products = []
            bundles = []

            for line in product_lines:
                fields = line.strip().split(',')
                if fields[0].startswith('P'):
                    ID = fields[0].strip()
                    name = fields[1].strip()
                    price = float(fields[2].strip())
                    prescription_required = fields[3].strip()
                    product = Product(ID, name, price, prescription_required)
                    individual_products.append(product)

                elif fields[0].startswith('B'):
                    ID = fields[0].strip()
                    name = fields[1].strip()
                    product_ids = [id.strip() for id in fields[2:]]
                    bundles.append((ID, name, product_ids))
            self.products.extend(individual_products)

            for bundle in bundles:
                ID, name, product_ids = bundle
                bundle_products = [prod for prod in individual_products if prod.ID in product_ids]
                if bundle_products:
                    bundle = Bundle(ID, name, bundle_products)
                    self.products.append(bundle)

            return True
        except FileNotFoundError:
            print(f"File not found: {file_name}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def read_orders(self, filename):
        if not os.path.isfile(filename):
            print(f"Order file '{filename}' not found.")
            return False

        try:
            with open(filename, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    print(f"Reading line {line_num}: {line.strip()}")
                    parts = line.strip().split(',')

                    if len(parts) < 5:
                        print(f"Invalid order line format: {line}. Skipping this order.")
                        continue

                    cust_info = parts[0].strip()
                    customer = self.find_customer(cust_info)
                    if not customer:
                        print(f"Customer '{cust_info}' not found. Skipping this order.")
                        continue

                    products_info = parts[1:-3]
                    try:
                        total_cost = float(parts[-3].strip())
                        earned_rewards = int(float(parts[-2].strip()))
                        timestamp = parts[-1].strip()
                    except ValueError as e:
                        print(f"Error parsing cost/reward/timestamp: {e}. Skipping this order.")
                        continue

                    product_quantities = []
                    for prod_info, quantity_str in zip(products_info[::2], products_info[1::2]):
                        prod_info = prod_info.strip()
                        quantity_str = quantity_str.strip()

                        try:
                            quantity = int(quantity_str)
                        except ValueError:
                            print(f"Invalid quantity '{quantity_str}' for product '{prod_info}'. Skipping this product in order.")
                            continue

                        product = self.find_product(prod_info)
                        if not product:
                            print(f"Product '{prod_info}' not found. Skipping this product in order.")
                            continue

                        product_quantities.append((product, quantity))

                    if product_quantities:
                        order = Order(customer, product_quantities, round(total_cost, 2), round(earned_rewards, 2), timestamp)
                        self.orders.append(order)
                        print(f"Order added: Customer {customer.name}, Products {product_quantities}, Total Cost {total_cost}, Earned Rewards {earned_rewards}, Timestamp {timestamp}")
                    else:
                        print(f"No valid products found for order: {line}")

            return True
        except Exception as e:
            print(f"An error occurred while reading the file: {filename} -> {e}")
            return False

    def write_customers(self, filename):
        try:
            with open(filename, 'w') as file:
                for customer in self.customers:
                    if isinstance(customer, BasicCustomer):
                        file.write(f"{customer.ID},{customer.name},{customer.reward},1.0\n")  # Reward is at index 2, reward rate is 1.0
                    elif isinstance(customer, VIPCustomer):
                        file.write(f"{customer.ID},{customer.name},{customer.reward},1.0,{customer.discount_rate}\n")  # Reward is at index 2, reward rate is 1.0
        except Exception as e:
            print(f"An error occurred while writing to the file: {filename} -> {e}")

    def write_products(self, filename):
        try:
            with open(filename, 'w') as file:
                for product in self.products:
                    if isinstance(product, Product):
                        prescription_text = 'y' if product.prescription_required else 'n'
                        file.write(f"{product.ID},{product.name},{product.price:.2f},{prescription_text}\n")
                    elif isinstance(product, Bundle):
                        product_ids = ','.join(prod.ID for prod in product.products)
                        file.write(f"{product.ID},{product.name},{product_ids},{product.price:.2f}\n")
        except Exception as e:
            print(f"An error occurred while writing to the file: {filename} -> {e}")

    def write_orders(self, filename):
        try:
            with open(filename, 'w') as file:
                for order in self.orders:
                    products_info = ','.join(f"{product.ID},{quantity}" for product, quantity in order.product_quantities)
                    file.write(f"{order.customer.ID},{products_info},{order.total_cost:.2f},{order.earned_rewards},{order.timestamp}\n")
        except Exception as e:
            print(f"An error occurred while writing to the file: {filename} -> {e}")

    def find_customer(self, search_value):
        search_value = search_value.strip().lower()
        for customer in self.customers:
            if search_value == customer.ID.lower() or search_value == customer.name.lower():
                return customer
        return None

    def find_product(self, product_name_or_product_ID):
        product_name_or_product_ID = product_name_or_product_ID.strip().lower()
        for product in self.products:
            if product_name_or_product_ID == product.ID.lower() or product_name_or_product_ID == product.name.lower():
                return product
        return None

    def add_or_update_product(self, ID_or_name, price, prescription_required):
        if isinstance(prescription_required, str):
            prescription_required = prescription_required.strip().lower() == 'y'

        product = self.find_product(ID_or_name.strip())
        if product:
            product.price = round(price, 2)  # Ensure price is rounded to two decimal points
            product.prescription_required = prescription_required
            print(f"Product {product.ID} updated.")
        else:
            max_id = max((int(p.ID[1:]) for p in self.products if p.ID.startswith('P')), default=0)
            new_id = f"P{max_id + 1}"
            new_product = Product(new_id, ID_or_name.strip(), round(price, 2), prescription_required)
            self.products.append(new_product)
            print(f"Product {new_id} added.")

    def list_customers(self):
        for customer in self.customers:
            customer.display_info()

    def list_products(self):
        if not self.products:
            print("No products available.")
        else:
            for product in self.products:
                product.display_info()

#create class Operations
class Operations:
    def __init__(self, records):
        self.records = records

    def make_purchase(self):
        while True:
            # ask the users to enter the customer name 
            customer_name = input("Enter customer name: ").lower()
            #user can enter only alphabet character
            if customer_name.isalpha():
                break
            else:
                print("Invalid customer. Enter alphabet character only")

        customer = self.records.find_customer(customer_name)
        if customer is None:
            print("Customer not found. Registering as a new Basic customer.")
            
            highest_id = 0
            for cust in self.records.customers:
                cust_id_number = int(cust.ID[1:])
                if cust_id_number > highest_id:
                    highest_id = cust_id_number
            
            new_id = f"B{highest_id + 1}"
            customer = BasicCustomer(new_id, customer_name, 0)
            self.records.customers.append(customer)
        else:
            if isinstance(customer, VIPCustomer):
                print(f"{customer.name} is a VIP Customer.")
            elif isinstance(customer, BasicCustomer):
                print(f"{customer.name} is a Basic customer.")

        while True:
            product_names = input("Enter product names separated by commas: ").split(',')
            product_names = [name.strip() for name in product_names]
            products = []

            for product_name in product_names:
                product = self.records.find_product(product_name)
                if product:
                    if product.prescription_required:
                        while True:
                            doctor_prescription = input(f"Do you have a doctor prescription for {product.name}? y/n: ").lower()
                            if doctor_prescription in ('y', 'n'):
                                if doctor_prescription == 'n':
                                    print(f"{product.name} requires a doctor prescription. Removing from order.")
                                    break
                                else:
                                    products.append(product)
                                    break
                            else:
                                print("Invalid input. Please enter 'y' or 'n'.")
                    else:
                        products.append(product)
                else:
                    print(f"Product not found: {product_name}. Please try again.")
                    break
            else:
                if products:
                    break
                else:
                    print("No valid products entered. Please try again.")

        while True:
            quantities = input("Enter quantities for each product separated by commas: ").split(',')
            try:
                quantities = [int(quantity.strip()) for quantity in quantities]
                if len(quantities) != len(products):
                    print("The number of quantities does not match the number of products. Please try again.")
                    continue
                if all(quantity > 0 for quantity in quantities):
                    break
                else:
                    print("All quantities must be positive numbers. Please try again.")
            except ValueError:
                print("Invalid input. Please enter numeric values.")

        product_quantities = list(zip(products, quantities))

        order = Order(customer, product_quantities, 0, 0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        total_cost_before_discount, discount, final_cost, reward = order.compute_cost()
        final_cost = order.deduct_rewards(final_cost)
        
        order.total_cost = final_cost
        order.earned_rewards = reward

        self.records.orders.append(order)

        print(f"Receipt\n{'-'*50}")
        print(f"Name:".ljust(20), f"{customer.name}")
        for product, quantity in product_quantities:
            print(f"Product:".ljust(20), product.name)
            print(f"Quantity:".ljust(20), quantity)
            print(f"Unit Price:".ljust(20), f"{product.price:.2f}" "(AUD)")
            print(f"{'-'*50}")
        if isinstance(customer, VIPCustomer):
            print(f"Original cost:".ljust(20), f"{total_cost_before_discount:.2f}" "(AUD)")
            print(f"Discount:".ljust(20), f"{discount:.2f}" "(AUD)")
        print(f"Total cost:".ljust(20), f"{final_cost:.2f}" "(AUD)")
        print(f"Earned reward:".ljust(20), reward)
        customer.update_reward(reward)


    def display_existing_customers(self):
        self.records.list_customers()

    def display_existing_products(self):
        if not self.records.products:
            print("No existing products found.")
        else:
            self.records.list_products()

    def add_update_information_of_product(self):
        input_str = input("Enter multiple product details in the format 'prod_name price doctor_prescription' separated by commas: ").strip()
        product_entries = input_str.split(',')
        for entry in product_entries:
            try:
                details = entry.strip().split()
                if len(details) != 3:
                    print(f"Invalid entry format for '{entry}'. Expected format: 'prod_name price doctor_prescription'")
                    continue
                ID_or_name = details[0]
                price = float(details[1])
                prescription_required = details[2].lower()

                self.records.add_or_update_product(ID_or_name, price, prescription_required)
            except ValueError as e:
                print(f"Error processing entry '{entry}': {e}")
            except IndexError:
                print(f"Invalid format for entry '{entry}'. Please use the format 'prod_name price doctor_prescription'.")

    def adjust_the_reward_rate_of_basic_customers(self):
        while True:
            try:
                rate = int(input("Enter new reward rate as an integer (e.g., enter 1 for 100%): ").strip())
                if rate <= 0:
                    raise ValueError("Reward rate must be a positive integer.")
                BasicCustomer.set_reward_rate(rate / 100.0)
                print(f"Basic customer reward rate set to {rate}%.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}. Please try again.")

    def adjust_the_discount_rate_of_a_VIP_customer(self):
        while True:
            customer_search = input("Enter VIP customer name or ID: ").strip().lower()
            customer = self.records.find_customer(customer_search)
            if customer is None or not isinstance(customer, VIPCustomer):
                print("Invalid VIP customer. Please enter a valid VIP customer name or ID.")
                continue
            while True:
                try:
                    rate = float(input("Enter new discount rate as a decimal (e.g., enter 0.2 for 20%): ").strip())
                    if rate <= 0:
                        raise ValueError("Discount rate must be a positive number.")
                    customer.set_discount_rate(rate)
                    print(f"VIP customer discount rate set to {rate * 100}%.")
                    break
                except ValueError as e:
                    print(f"Invalid input: {e}. Please try again.")
            break

    def display_all_orders(self):
        if not self.records.orders:
            print("No orders available.")
        else:
            for order in self.records.orders:
                customer_name = order.customer.name
                for product, quantity in order.product_quantities:
                    print(f"Customer: {customer_name}, Product: {product.name}, Quantity: {quantity}, Date: {order.timestamp}")

    def display_customer_order_history(self):
        customer_search = input("Enter customer name or ID: ").strip().lower()
        customer = self.records.find_customer(customer_search)
        if customer is None:
            print("Customer not found.")
            return

        customer_orders = [order for order in self.records.orders if order.customer == customer]
        if not customer_orders:
            print("No orders found for this customer.")
            return

        print(f"This is the order history of {customer.name.capitalize()}.")
        print(f"{'Order':<8}{'Products':<40}{'Total Cost':<15}{'Earned Rewards'}")
        for i, order in enumerate(customer_orders, 1):
            products_info = ', '.join([f"{quantity} x {product.name}" for product, quantity in order.product_quantities])
            print(f"{'Order ' + str(i):<8}{products_info:<40}{order.total_cost:<15.2f}{order.earned_rewards}")

    def exit_program(self):
        customers_file = 'customers.txt'
        products_file = 'products.txt'
        order_file = 'orders.txt'
        
        self.records.write_customers(customers_file)
        self.records.write_products(products_file)
        self.records.write_orders(order_file)

        print("Data saved. Exiting the program")
        exit()


def main():
    records = Record()

    customers_file = 'customers.txt'
    products_file = 'products.txt'
    order_file = 'orders.txt'

    if not (records.read_customers(customers_file) and records.read_products(products_file) and records.read_orders(order_file)):
        print("Please ensure that the customers, products, and orders files are present and correctly formatted.")
        return

    operations = Operations(records)

    while True:
        print("\nMenu:")
        print("1. Make a purchase")
        print("2. Display existing customers")
        print("3. Display existing products")
        print("4. Add or update product information")
        print("5. Adjust the reward rate of basic customers")
        print("6. Adjust the discount rate of a VIP customer")
        print("7. Display all orders")
        print("8. Display customer order history")
        print("9. Exit the program")

        choice = input("Enter your choice: ")

        if choice == '1':
            operations.make_purchase()
        elif choice == '2':
            operations.display_existing_customers()
        elif choice == '3':
            operations.display_existing_products()
        elif choice == '4':
            operations.add_update_information_of_product()
        elif choice == '5':
            operations.adjust_the_reward_rate_of_basic_customers()
        elif choice == '6':
            operations.adjust_the_discount_rate_of_a_VIP_customer()
        elif choice == '7':
            operations.display_all_orders()
        elif choice == '8':
            operations.display_customer_order_history()
        elif choice == '9':
            operations.exit_program()
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()

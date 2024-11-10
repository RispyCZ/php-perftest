from locust import HttpUser, task, between
import random
import json

class UserLoadTest(HttpUser):
    # Wait between 1 and 3 seconds between tasks
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_user_ids = []
        
    def on_start(self):
        """Initialize test data"""
        self.test_users = [
            {
                "firstname": f"John{i}",
                "lastname": f"Doe{i}",
                "address": f"{i} Main St, City {i}, Country"
            }
            for i in range(100)
        ]

    @task(3)  # Higher weight for creation
    def create_user(self):
        """Test POST endpoint for user creation"""
        # Randomly select a test user
        user_data = random.choice(self.test_users)
        
        # Make POST request
        with self.client.post("/", data=user_data, catch_response=True) as response:
            try:
                result = response.json()
                if response.status_code == 200 and result.get('success'):
                    user_id = result.get('id')
                    if user_id:
                        self.created_user_ids.append(user_id)
                    response.success()
                else:
                    response.failure(f"Failed to create user: {result}")
            except json.JSONDecodeError:
                response.failure("Invalid JSON response")

    @task(2)  # Lower weight for retrieval
    def get_user(self):
        """Test GET endpoint for user retrieval"""
        if not self.created_user_ids:
            return
            
        # Randomly select a user ID
        user_id = random.choice(self.created_user_ids)
        
        # Make GET request
        with self.client.get(f"/?id={user_id}", catch_response=True) as response:
            try:
                result = response.json()
                if response.status_code == 200 and 'error' not in result:
                    response.success()
                else:
                    response.failure(f"Failed to retrieve user: {result}")
            except json.JSONDecodeError:
                response.failure("Invalid JSON response")

    @task(1)  # Lowest weight for invalid requests
    def test_invalid_request(self):
        """Test invalid requests"""
        # Test invalid GET request
        with self.client.get("/?id=999999", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
            else:
                response.failure("Expected 404 for invalid user")
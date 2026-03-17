    def test_connection(self) -> dict:
        """Test API connection and return available data"""
        print("Testing GoHighLevel API connection...")
        print(f"  API Key: {self.api_key[:10]}...")
        print(f"  Location ID: {self.location_id}")
        
        # Try to get contacts
        endpoint = f"{self.base_url}/v1/contacts"
        params = {"limit": 1}
        
        if self.location_id:
            params["location_id"] = self.location_id
            
        try:
            response = self._session.get(endpoint, params=params, timeout=self.timeout)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Response keys: {list(data.keys())}")
                if "contacts" in data:
                    print(f"  Total contacts available: {data.get('total', 'unknown')}")
                return {"success": True, "data": data}
            else:
                print(f"  Error: {response.text[:200]}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"  Exception: {e}")
            return {"success": False, "error": str(e)}
#!/usr/bin/env python3
"""
Nuwa Backend Test Script

Quick test script to verify FastAPI backend functionality.
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_PROJECT = {
    "name": "Amazon Reforestation Test Project",
    "description": "Test carbon capture project for Amazon rainforest restoration",
    "project_type": "reforestation",
    "country": "Brazil",
    "region": "Amazonas", 
    "latitude": -3.4653,
    "longitude": -62.2159,
    "project_area_hectares": 1000.0,
    "estimated_co2_capture_tons_year": 5000.0,
    "methodology": "AR-ACM0003",
    "standard": "VCS"
}

class NuwaBackendTester:
    """Test class for Nuwa backend functionality."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = None
        self.test_project_id = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_health_check(self) -> bool:
        """Test basic health check endpoints."""
        print("🏥 Testing health check endpoints...")
        
        try:
            # Test root endpoint
            response = await self.client.get("/")
            print(f"  Root endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    Status: {data.get('status')}")
                print(f"    Version: {data.get('version')}")
            
            # Test health endpoint
            response = await self.client.get("/health")
            print(f"  Health endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    Status: {data.get('status')}")
                print(f"    Uptime: {data.get('uptime')}")
            
            # Test API health
            response = await self.client.get("/api/v1/health/")
            print(f"  API health endpoint: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Health check failed: {str(e)}")
            return False
    
    async def test_detailed_health(self) -> bool:
        """Test detailed health check including database."""
        print("🔍 Testing detailed health check...")
        
        try:
            response = await self.client.get("/api/v1/health/detailed")
            print(f"  Detailed health: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    Overall status: {data.get('status')}")
                print(f"    Environment: {data.get('environment')}")
                
                services = data.get('services', {})
                for service, status in services.items():
                    if isinstance(status, dict):
                        service_status = status.get('status', 'unknown')
                        print(f"    {service}: {service_status}")
                    else:
                        print(f"    {service}: {status}")
                
                return data.get('status') in ['healthy', 'degraded']
            
            return False
            
        except Exception as e:
            print(f"  ❌ Detailed health check failed: {str(e)}")
            return False
    
    async def test_project_creation(self) -> bool:
        """Test project creation endpoint."""
        print("🌱 Testing project creation...")
        
        try:
            response = await self.client.post("/api/v1/projects/", json=TEST_PROJECT)
            print(f"  Project creation: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.test_project_id = data.get('id')
                print(f"    Created project ID: {self.test_project_id}")
                print(f"    Project name: {data.get('name')}")
                print(f"    Project type: {data.get('project_type')}")
                return True
            else:
                print(f"    Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ❌ Project creation failed: {str(e)}")
            return False
    
    async def test_project_retrieval(self) -> bool:
        """Test project retrieval endpoints."""
        print("📋 Testing project retrieval...")
        
        if not self.test_project_id:
            print("  ⚠️ No test project ID available")
            return False
        
        try:
            # Test get single project
            response = await self.client.get(f"/api/v1/projects/{self.test_project_id}")
            print(f"  Get project: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    Retrieved project: {data.get('name')}")
            
            # Test list projects
            response = await self.client.get("/api/v1/projects/?limit=5")
            print(f"  List projects: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    Total projects: {data.get('total')}")
                print(f"    Returned projects: {len(data.get('projects', []))}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Project retrieval failed: {str(e)}")
            return False
    
    async def test_evaluation_creation(self) -> bool:
        """Test evaluation creation."""
        print("🔬 Testing evaluation creation...")
        
        if not self.test_project_id:
            print("  ⚠️ No test project ID available")
            return False
        
        try:
            evaluation_data = {
                "project_id": self.test_project_id,
                "evaluation_type": "baseline",
                "evaluation_date": datetime.utcnow().isoformat(),
                "satellite_data_sources": ["sentinel-2"],
                "analysis_method": "test_analysis"
            }
            
            response = await self.client.post("/api/v1/evaluations/", json=evaluation_data)
            print(f"  Evaluation creation: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"    Created evaluation ID: {data.get('id')}")
                print(f"    Evaluation type: {data.get('evaluation_type')}")
                return True
            else:
                print(f"    Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ❌ Evaluation creation failed: {str(e)}")
            return False
    
    async def test_api_documentation(self) -> bool:
        """Test API documentation endpoints."""
        print("📖 Testing API documentation...")
        
        try:
            # Test OpenAPI schema
            response = await self.client.get("/openapi.json")
            print(f"  OpenAPI schema: {response.status_code}")
            
            # Test Swagger UI
            response = await self.client.get("/docs")
            print(f"  Swagger UI: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ API documentation test failed: {str(e)}")
            return False
    
    async def cleanup_test_data(self) -> bool:
        """Clean up test data."""
        print("🧹 Cleaning up test data...")
        
        if not self.test_project_id:
            return True
        
        try:
            response = await self.client.delete(f"/api/v1/projects/{self.test_project_id}")
            print(f"  Delete test project: {response.status_code}")
            return response.status_code in [200, 204, 404]
            
        except Exception as e:
            print(f"  ⚠️ Cleanup failed: {str(e)}")
            return False

async def run_backend_tests():
    """Run comprehensive backend tests."""
    print("🚀 Starting Nuwa Backend Tests")
    print("=" * 50)
    
    test_results = []
    
    async with NuwaBackendTester() as tester:
        # Run tests in sequence
        tests = [
            ("Health Check", tester.test_health_check),
            ("Detailed Health", tester.test_detailed_health),
            ("Project Creation", tester.test_project_creation),
            ("Project Retrieval", tester.test_project_retrieval),
            ("Evaluation Creation", tester.test_evaluation_creation),
            ("API Documentation", tester.test_api_documentation),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                test_results.append((test_name, result))
                if result:
                    print(f"✅ {test_name}: PASSED\n")
                else:
                    print(f"❌ {test_name}: FAILED\n")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}\n")
                test_results.append((test_name, False))
        
        # Cleanup
        await tester.cleanup_test_data()
    
    # Print summary
    print("📊 Test Summary")
    print("=" * 50)
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the backend configuration.")
        return False

if __name__ == "__main__":
    import sys
    
    print("Nuwa Backend Test Suite")
    print("Make sure the backend is running on http://localhost:8000")
    print()
    
    try:
        result = asyncio.run(run_backend_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        sys.exit(1)
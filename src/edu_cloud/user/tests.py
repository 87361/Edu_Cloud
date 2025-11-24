"""
Comprehensive test cases for the Flask User API
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from main import create_app
from src.edu_cloud.user.models import User
from src.edu_cloud.user.schemas import UserCreate, UserLogin, UserUpdate
from src.edu_cloud.common.database import SessionLocal
from src.edu_cloud.common.security import get_password_hash


class TestUserAPI:
    """Test class for User API endpoints"""
    
    def setup_method(self):
        """Setup test client and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
        
        # Setup test database
        self.db_session = SessionLocal()
        
        # Create test user
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            hashed_password=get_password_hash('testpass123'),
            is_active=True
        )
        self.db_session.add(self.test_user)
        self.db_session.commit()
        
    def teardown_method(self):
        """Cleanup after each test"""
        self.db_session.query(User).delete()
        self.db_session.commit()
        self.db_session.close()
    
    def test_register_success(self):
        """Test successful user registration"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/user/register', 
                                data=json.dumps(user_data),
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert data['data']['username'] == 'newuser'
        assert data['data']['email'] == 'newuser@example.com'
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        user_data = {
            'username': 'testuser',  # Already exists
            'email': 'another@example.com',
            'full_name': 'Another User',
            'password': 'password123'
        }
        
        response = self.client.post('/api/user/register',
                                data=json.dumps(user_data),
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Username already registered' in data['error']
    
    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        user_data = {
            'username': '',  # Invalid empty username
            'email': 'invalid-email',  # Invalid email
            'password': '123'  # Too short password
        }
        
        response = self.client.post('/api/user/register',
                                data=json.dumps(user_data),
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Validation error' in data['error']
    
    def test_login_success(self):
        """Test successful user login"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/user/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/user/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Incorrect username or password' in data['error']
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        # Create inactive user
        inactive_user = User(
            username='inactiveuser',
            email='inactive@example.com',
            hashed_password=get_password_hash('password123'),
            is_active=False
        )
        self.db_session.add(inactive_user)
        self.db_session.commit()
        
        login_data = {
            'username': 'inactiveuser',
            'password': 'password123'
        }
        
        response = self.client.post('/api/user/login',
                                data=json.dumps(login_data),
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Inactive user' in data['error']
    
    def test_get_user_info_success(self):
        """Test getting current user info with valid token"""
        # First login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post('/api/user/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        
        # Get user info
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/user/me', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert data['data']['username'] == 'testuser'
        assert data['data']['email'] == 'test@example.com'
    
    def test_get_user_info_invalid_token(self):
        """Test getting user info with invalid token"""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = self.client.get('/api/user/me', headers=headers)
        
        assert response.status_code == 401
    
    def test_get_user_info_no_token(self):
        """Test getting user info without token"""
        response = self.client.get('/api/user/me')
        
        assert response.status_code == 401
    
    def test_update_user_info_success(self):
        """Test updating user info successfully"""
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post('/api/user/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        
        # Update user info
        update_data = {
            'full_name': 'Updated Name',
            'email': 'updated@example.com'
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.put('/api/user/me',
                                data=json.dumps(update_data),
                                content_type='application/json',
                                headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert data['data']['full_name'] == 'Updated Name'
        assert data['data']['email'] == 'updated@example.com'
    
    def test_change_password_success(self):
        """Test successful password change"""
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post('/api/user/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        
        # Change password
        password_data = {
            'current_password': 'testpass123',
            'new_password': 'newpassword123'
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/user/change-password',
                                 data=json.dumps(password_data),
                                 content_type='application/json',
                                 headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Password changed successfully' in data['message']
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post('/api/user/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        
        # Try to change password with wrong current password
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/user/change-password',
                                 data=json.dumps(password_data),
                                 content_type='application/json',
                                 headers=headers)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Current password is incorrect' in data['error']
    
    def test_logout_success(self):
        """Test successful logout"""
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post('/api/user/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        
        # Logout
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/api/user/logout', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Successfully logged out' in data['message']
    
    def test_get_users_list_success(self):
        """Test getting users list"""
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post('/api/user/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        
        # Get users list
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/user/', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 1  # At least our test user
    
    def test_delete_user_success(self):
        """Test successful user deletion"""
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post('/api/user/login',
                                     data=json.dumps(login_data),
                                     content_type='application/json')
        token = json.loads(login_response.data)['access_token']
        
        # Delete user
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete('/api/user/me', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'User account deleted successfully' in data['message']
    
    def test_error_response_format(self):
        """Test that error responses have consistent format"""
        response = self.client.post('/api/user/login',
                                data=json.dumps({'invalid': 'data'}),
                                content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert isinstance(data['error'], str)

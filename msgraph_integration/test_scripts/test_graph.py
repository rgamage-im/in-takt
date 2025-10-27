"""
Test Microsoft Graph Integration
Run this script to test the MS Graph API integration
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from msgraph_integration.services import GraphService


def test_graph_connection():
    """Test basic Microsoft Graph connection"""
    print("Testing Microsoft Graph API Connection...")
    print("-" * 50)
    
    # Check environment variables
    client_id = os.getenv('MICROSOFT_GRAPH_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_GRAPH_CLIENT_SECRET')
    tenant_id = os.getenv('MICROSOFT_GRAPH_TENANT_ID')
    
    if not all([client_id, client_secret]):
        print("❌ ERROR: Microsoft Graph credentials not configured!")
        print("\nPlease set these environment variables in your .env file:")
        print("  - MICROSOFT_GRAPH_CLIENT_ID")
        print("  - MICROSOFT_GRAPH_CLIENT_SECRET")
        print("  - MICROSOFT_GRAPH_TENANT_ID (optional, defaults to 'common')")
        return False
    
    print("✅ Environment variables configured")
    print(f"   Client ID: {client_id[:10]}...")
    print(f"   Tenant ID: {tenant_id or 'common'}")
    print()
    
    # Test connection
    try:
        print("Attempting to connect to Microsoft Graph...")
        service = GraphService()
        
        print("✅ GraphService initialized")
        
        # Try to get a token
        print("Requesting access token...")
        token = service._get_access_token()
        
        if token:
            print("✅ Successfully obtained access token")
            print(f"   Token (first 20 chars): {token[:20]}...")
            print()
            
            # Try to list users
            print("Attempting to list users...")
            users = service.list_users(top=5)
            
            user_count = len(users.get('value', []))
            print(f"✅ Successfully retrieved {user_count} users")
            
            if user_count > 0:
                print("\nFirst user:")
                first_user = users['value'][0]
                print(f"  - Display Name: {first_user.get('displayName')}")
                print(f"  - Email: {first_user.get('mail') or first_user.get('userPrincipalName')}")
                print(f"  - Job Title: {first_user.get('jobTitle', 'N/A')}")
            
            print("\n" + "=" * 50)
            print("✅ Microsoft Graph integration is working!")
            print("=" * 50)
            print("\nYou can now:")
            print("1. Start the dev server: python manage.py runserver")
            print("2. Visit: http://localhost:8000/api/docs/")
            print("3. Test the API endpoints")
            
            return True
        else:
            print("❌ Failed to obtain access token")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\nCommon issues:")
        print("1. Invalid client ID or secret")
        print("2. Incorrect tenant ID")
        print("3. App registration doesn't have required permissions")
        print("   Required: User.Read.All (Application permission)")
        print("4. Admin consent not granted for the permissions")
        return False


if __name__ == "__main__":
    test_graph_connection()

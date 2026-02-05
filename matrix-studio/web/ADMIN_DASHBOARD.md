# Admin Dashboard Documentation

## Overview
A comprehensive admin dashboard for managing users, billing, and system analytics.

## Access
**Login Credentials:**
- Username: `admin`
- Password: `admin123`
- Navigate to: `http://localhost:5173/?admin=true`

## Features

### Dashboard Tab
- **User Statistics:** Total users, active users (last 7 days)
- **Revenue Analytics:** Total revenue, monthly revenue, balance
- **Transaction Metrics:** Success rate, total/failed transactions
- **Plan Distribution:** User breakdown by subscription plans

### Users Management Tab
- **User Listing:** Paginated table with all registered users
- **Search & Filter:** Search by username/email, filter by plan
- **Plan Management:** Change user plans in real-time
- **User Details:** Modal view with comprehensive user information
- **User Actions:** View details, edit, delete users

### Backend API Endpoints
All endpoints require admin authentication via Bearer token.

**Analytics:**
- `GET /api/admin/analytics` - System-wide analytics and metrics

**User Management:**
- `GET /api/admin/users?page=1&limit=10&search=&plan=` - List users with pagination and filtering
- `GET /api/admin/users/:id` - Get specific user details
- `PUT /api/admin/users/:id` - Update user (plan, email)
- `DELETE /api/admin/users/:id` - Delete user

## Security Features
- JWT-based admin authentication
- Middleware protection for all admin routes
- Role-based access control (admin only)
- Token validation on every request

## Data Management
- Mock data for demonstration (replace with database)
- Real Stripe integration for payment analytics
- Responsive pagination for large user sets
- Real-time plan updates without page refresh

## UI/UX
- Responsive design with mobile support
- Loading states and error handling
- Confirmation dialogs for destructive actions
- Consistent theming with brand colors
- Modal-based user detail views

## Next Steps for Production
1. Replace mock data with database integration
2. Add user activity logging
3. Implement bulk user operations
4. Add export functionality (CSV, PDF)
5. Set up automated user notifications
6. Add subscription management
7. Implement webhooks for real-time updates
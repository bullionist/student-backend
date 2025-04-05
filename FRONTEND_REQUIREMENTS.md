# AI-Powered Student Counseling Platform - Frontend Requirements

## Project Overview
The AI-Powered Student Counseling Platform is a web application that helps students receive personalized counseling and program recommendations. The platform uses AI (via Groq API) to analyze student inputs and provide structured guidance.

## Technical Stack Requirements
- React/Next.js for the frontend framework
- TypeScript for type safety
- Supabase Client for authentication and data management
- Material-UI or Tailwind CSS for styling
- React Query for API state management
- Axios or fetch for API calls

## Authentication
- Implement Supabase Email OTP authentication
- Protected routes for authenticated users
- Admin role-based access control
- Session management and token handling

### Admin Authentication
```typescript
// Admin login request and response types
interface AdminLoginRequest {
  email: string;
  password: string;
}

interface AdminLoginResponse {
  id: string;
  email: string;
  access_token: string;
  token_type: string;
}

// Admin login function
const loginAdmin = async (email: string, password: string): Promise<AdminLoginResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/admin/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  const data = await response.json();
  // Store the token in localStorage or secure storage
  localStorage.setItem('adminToken', data.access_token);
  return data;
};
```

### Protected Admin Routes
```typescript
// ProtectedRoute component for admin routes
const ProtectedAdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('adminToken');
  
  if (!token) {
    return <Navigate to="/admin/login" replace />;
  }

  return <>{children}</>;
};

// Usage in routing
<Routes>
  <Route path="/admin/login" element={<AdminLogin />} />
  <Route
    path="/admin/programs"
    element={
      <ProtectedAdminRoute>
        <ProgramsList />
      </ProtectedAdminRoute>
    }
  />
  {/* Other protected routes */}
</Routes>
```

### API Service with Authentication
```typescript
// api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Add request interceptor to add token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('adminToken');
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);
```

## Core Features

### 1. Student Dashboard
- Student profile management
- Conversation history with AI counselor
- Program recommendations display
- Academic background information
- Preferred location and field of study preferences

### 2. Program Management (Admin Only)
- CRUD operations for educational programs
- Program listing and filtering
- Program details view
- Program analytics

### 3. AI Counseling Interface
- Real-time chat interface with AI
- Input analysis and structured data extraction
- Progress tracking
- Session history

## API Integration

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints
```
POST   /api/admin/login      - Admin login
POST   /api/admin/register   - Register new admin (admin only)
GET    /api/admin/me         - Get current admin profile
```

### Program Endpoints (All require admin authentication)
```
GET    /api/programs          - List all programs
POST   /api/programs          - Create new program
GET    /api/programs/{id}     - Get program details
PUT    /api/programs/{id}     - Update program
DELETE /api/programs/{id}     - Delete program

// Required headers for all program endpoints
headers: {
  'Authorization': 'Bearer <admin_token>'
}
```

### Student Endpoints
```
POST   /api/students          - Create new student session
GET    /api/students/{id}     - Get student details
POST   /api/students/{id}/analyze - Analyze student input
```

## Data Models

### Program
```typescript
interface Program {
  id: string;
  program_title: string;
  institution: string;
  program_overview: string;
  eligibility_criteria: {
    qualifications: string[];
    experience?: string;
    age_limit?: string;
    other_requirements: string[];
  };
  duration: string;
  fees: number;
  curriculum: {
    core_modules: Array<{
      name: string;
      description?: string;
      credits?: number;
    }>;
    elective_modules?: Array<{
      name: string;
      description?: string;
      credits?: number;
    }>;
  };
  mode_of_delivery: string;
  application_details: string;
  location: string;
  additional_notes?: string;
}
```

### Student
```typescript
interface Student {
  id: string;
  academic_background?: string;
  preferred_location?: string;
  field_of_study?: string;
  exam_scores?: Record<string, number>;
  additional_preferences?: string;
  conversation_history: {
    messages: Array<{
      role: 'user' | 'assistant' | 'system';
      content: string;
      timestamp: string;
    }>;
  };
}
```

## UI/UX Requirements

### Responsive Design
- Mobile-first approach
- Breakpoints: xs, sm, md, lg, xl
- Fluid layouts
- Touch-friendly interfaces


### Performance
- Lazy loading of components
- Image optimization
- Caching strategies
- Progressive Web App capabilities

### Error Handling
- User-friendly error messages
- Offline support
- Loading states
- Retry mechanisms

## State Management
- Global state for user authentication
- Local state for form handling
- Cache management for API responses
- Real-time updates for chat
- Admin authentication state management


## Security Considerations
- Secure storage of tokens (preferably HttpOnly cookies in production)
- XSS prevention
- CSRF protection
- Input sanitization
- Secure communication with backend
- Token expiration and refresh handling
- Admin session management

## Development Workflow
1. Set up development environment
2. Implement authentication flow
3. Create core components
4. Integrate with backend APIs
5. Add AI counseling features
6. Implement admin features
7. Add testing
8. Performance optimization
9. Documentation

## Environment Setup
Required environment variables:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment Considerations
- CI/CD pipeline setup
- Environment-specific configurations
- Monitoring and logging
- Backup strategies
- Performance monitoring
- Error tracking

## Documentation Requirements
- Component documentation
- API integration guide
- Setup instructions
- Deployment guide
- Contributing guidelines
- User guide 
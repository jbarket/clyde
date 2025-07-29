# Next.js Patterns and Best Practices

## Server Components vs Client Components

### Server Components (Default)
```tsx
// app/users/page.tsx - Server Component
import { getUsers } from '@/lib/users';
import { UserList } from '@/components/UserList';

// This runs on the server
export default async function UsersPage() {
  const users = await getUsers(); // Direct database access
  
  return (
    <div>
      <h1>Users</h1>
      <UserList users={users} />
    </div>
  );
}
```

### Client Components
```tsx
'use client';

import { useState, useEffect } from 'react';
import { User } from '@/types';

// This runs on the client
export function InteractiveUserList({ initialUsers }: { initialUsers: User[] }) {
  const [users, setUsers] = useState(initialUsers);
  const [filter, setFilter] = useState('');

  const filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      <input
        type="text"
        placeholder="Filter users..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      {filteredUsers.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

## Data Fetching Patterns

### Server-Side Data Fetching
```tsx
// Static data at build time
export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

// Dynamic data on each request
export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await getPost(params.slug);
  
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}

// With error handling
export default async function UserPage({ params }: { params: { id: string } }) {
  try {
    const user = await getUser(params.id);
    return <UserProfile user={user} />;
  } catch (error) {
    console.error('Failed to fetch user:', error);
    return <div>Failed to load user</div>;
  }
}
```

### Client-Side Data Fetching with SWR
```tsx
'use client';

import useSWR from 'swr';
import { User } from '@/types';

const fetcher = (url: string) => fetch(url).then(res => res.json());

export function UserProfile({ userId }: { userId: string }) {
  const { data: user, error, isLoading, mutate } = useSWR<User>(
    `/api/users/${userId}`,
    fetcher
  );

  if (error) return <div>Failed to load</div>;
  if (isLoading) return <div>Loading...</div>;
  if (!user) return <div>No user data</div>;

  const handleUpdate = async (updates: Partial<User>) => {
    // Optimistic update
    mutate({ ...user, ...updates }, false);
    
    try {
      await fetch(`/api/users/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      // Revalidate
      mutate();
    } catch (error) {
      // Revert on error
      mutate();
    }
  };

  return (
    <div>
      <h1>{user.name}</h1>
      <button onClick={() => handleUpdate({ name: 'Updated Name' })}>
        Update Name
      </button>
    </div>
  );
}
```

## Authentication Patterns

### Middleware for Route Protection
```tsx
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { verifyAuth } from '@/lib/auth';

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;
  
  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token || !(await verifyAuth(token))) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }
  
  // Redirect authenticated users away from auth pages
  if (request.nextUrl.pathname.startsWith('/login') || 
      request.nextUrl.pathname.startsWith('/register')) {
    if (token && (await verifyAuth(token))) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/register']
};
```

### Session Management
```tsx
// lib/auth.ts
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import jwt from 'jsonwebtoken';

export async function getSession() {
  const token = cookies().get('auth-token')?.value;
  
  if (!token) {
    return null;
  }
  
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as any;
    return { userId: payload.sub, ...payload };
  } catch {
    return null;
  }
}

export async function requireAuth() {
  const session = await getSession();
  
  if (!session) {
    redirect('/login');
  }
  
  return session;
}

// Usage in pages
export default async function DashboardPage() {
  const session = await requireAuth();
  
  return (
    <div>
      <h1>Welcome, {session.email}!</h1>
    </div>
  );
}
```

## Form Handling Patterns

### Server Actions
```tsx
// app/users/new/page.tsx
import { createUser } from '@/lib/actions';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

async function handleCreateUser(formData: FormData) {
  'use server';
  
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;
  
  try {
    await createUser({ name, email });
    revalidatePath('/users');
    redirect('/users');
  } catch (error) {
    // Handle error
    throw error;
  }
}

export default function NewUserPage() {
  return (
    <form action={handleCreateUser}>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <button type="submit">Create User</button>
    </form>
  );
}
```

### Progressive Enhancement with useFormState
```tsx
'use client';

import { useFormState } from 'react-dom';
import { createUser } from '@/lib/actions';

interface FormState {
  message?: string;
  errors?: Record<string, string[]>;
}

const initialState: FormState = {};

export function UserForm() {
  const [state, formAction] = useFormState(createUser, initialState);
  
  return (
    <form action={formAction}>
      <div>
        <input name="name" placeholder="Name" />
        {state.errors?.name && (
          <p className="text-red-500">{state.errors.name[0]}</p>
        )}
      </div>
      
      <div>
        <input name="email" type="email" placeholder="Email" />
        {state.errors?.email && (
          <p className="text-red-500">{state.errors.email[0]}</p>
        )}
      </div>
      
      {state.message && (
        <p className="text-green-500">{state.message}</p>
      )}
      
      <button type="submit">Create User</button>
    </form>
  );
}
```
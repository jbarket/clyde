# Problem Decomposition Patterns

## Core Principle

Problem decomposition involves breaking complex challenges into smaller, manageable components that can be understood, solved, and verified independently while maintaining awareness of their relationships and interactions.

## When to Apply

- Large, overwhelming problems that seem intractable
- Requirements that are vague or constantly changing
- Technical challenges spanning multiple domains
- Projects involving multiple teams or stakeholders
- Debugging complex, multi-layered issues

## Decomposition Strategies

### 1. Hierarchical Decomposition
Break problems into levels of increasing detail:

```
Application Slow → 
├── Frontend Performance
│   ├── Bundle Size
│   ├── Rendering Speed
│   └── Asset Loading
├── Backend Performance  
│   ├── API Response Time
│   ├── Database Queries
│   └── Server Resources
└── Infrastructure
    ├── Network Latency
    ├── CDN Configuration
    └── Server Capacity
```

### 2. Functional Decomposition
Separate by what the system needs to do:

```
E-commerce Platform →
├── User Management (auth, profiles, preferences)
├── Product Catalog (search, display, inventory)
├── Shopping Cart (add, modify, persistence)
├── Payment Processing (validation, transactions, receipts)
├── Order Management (tracking, fulfillment, returns)
└── Analytics (user behavior, sales data, reports)
```

### 3. Domain-Driven Decomposition
Organize by business domains and their boundaries:

```
Healthcare System →
├── Patient Management Domain
├── Appointment Scheduling Domain  
├── Medical Records Domain
├── Billing and Insurance Domain
├── Pharmacy Management Domain
└── Reporting and Analytics Domain
```

### 4. Temporal Decomposition
Break down by when things happen:

```
User Registration Flow →
├── Pre-Registration (marketing, landing page)
├── Registration Process (form, validation, verification)
├── Initial Setup (profile creation, preferences)
├── Onboarding (tutorials, first actions)
└── Post-Registration (engagement, retention)
```

### 5. Risk-Based Decomposition
Separate by uncertainty and complexity:

```
Migration Project →
├── High Risk/High Impact
│   ├── Data migration strategy
│   └── Authentication system changes
├── Medium Risk/High Impact
│   ├── API endpoint updates
│   └── Database schema changes
├── Low Risk/High Impact
│   ├── UI updates
│   └── Configuration changes
└── Low Risk/Low Impact
    ├── Documentation updates
    └── Monitoring adjustments
```

## Decomposition Process

### Phase 1: Initial Breakdown
1. **State the problem clearly** in one sentence
2. **Identify major components** - aim for 3-7 main parts
3. **Define boundaries** between components
4. **List assumptions** about each component
5. **Note interdependencies** between parts

### Phase 2: Iterative Refinement
1. **Examine each component** - can it be broken down further?
2. **Look for patterns** - are similar problems grouped together?
3. **Check completeness** - does the sum cover the whole problem?
4. **Validate boundaries** - are the divisions logical and workable?
5. **Prioritize components** by impact, risk, and dependencies

### Phase 3: Integration Planning
1. **Map dependencies** between components
2. **Identify integration points** where components interact
3. **Plan coordination** mechanisms between parts
4. **Define success criteria** for each component and the whole
5. **Create feedback loops** to detect when assumptions change

## Examples

### Example 1: API Performance Problem

**Initial Problem**: "API is too slow"

**Decomposition**:
```
API Performance →
├── Request Processing
│   ├── Route matching speed
│   ├── Middleware overhead
│   └── Request validation time
├── Business Logic
│   ├── Algorithm efficiency
│   ├── External service calls
│   └── Computation complexity
├── Data Access
│   ├── Database query performance
│   ├── Connection pool management
│   └── Cache hit rates
└── Response Generation
    ├── Serialization speed
    ├── Response size
    └── Compression efficiency
```

**Integration Considerations**:
- Database optimizations might affect business logic assumptions
- Caching changes could impact data consistency requirements
- Response format changes might affect client applications

### Example 2: Team Productivity Problem

**Initial Problem**: "Development team is moving too slowly"

**Decomposition**:
```
Team Productivity →
├── Process Issues
│   ├── Meeting overhead
│   ├── Code review bottlenecks
│   └── Deployment friction
├── Technical Issues
│   ├── Legacy code complexity
│   ├── Testing infrastructure
│   └── Development environment setup
├── Communication Issues
│   ├── Requirements clarity
│   ├── Cross-team coordination
│   └── Knowledge sharing
└── Resource Issues
    ├── Team capacity
    ├── Skill gaps
    └── Tool limitations
```

## Quality Checks

### Completeness Check
- **Coverage**: Do all components together solve the original problem?
- **Gaps**: Are there aspects of the problem not addressed?
- **Overlap**: Are responsibilities clearly separated?

### Feasibility Check
- **Size**: Is each component small enough to understand and solve?
- **Skills**: Do we have the expertise to address each component?
- **Resources**: Are the components achievable with available resources?

### Dependency Check
- **Prerequisites**: What must be completed before each component?
- **Blockers**: Which components might prevent others from succeeding?
- **Coordination**: How will components work together?

## Tools and Techniques

### Mind Mapping
- Visual representation of problem structure
- Shows relationships and hierarchies clearly
- Helps identify missing components
- Good for brainstorming and initial decomposition

### Work Breakdown Structure (WBS)
- Formal project management technique
- Organizes work into deliverable components
- Includes effort estimation and scheduling
- Good for project planning and tracking

### System Context Diagrams
- Shows system boundaries and external interfaces
- Identifies stakeholders and external dependencies
- Helps understand scope and constraints
- Good for complex systems with many interactions

### Dependency Matrices
- Maps relationships between components
- Identifies critical path and bottlenecks
- Shows coordination requirements
- Good for understanding integration complexity

## Anti-patterns to Avoid

- **Over-Decomposition**: Breaking things down beyond useful granularity
- **Under-Decomposition**: Components still too complex to handle effectively
- **Arbitrary Boundaries**: Divisions that don't reflect natural problem structure
- **Ignoring Dependencies**: Treating components as if they're completely independent
- **Static Decomposition**: Not updating breakdown as understanding evolves
- **Perfect Decomposition Fallacy**: Spending too much time on perfect structure instead of starting work

## Benefits

- **Cognitive Load Reduction**: Smaller problems are easier to understand and solve
- **Parallel Work**: Independent components can be worked on simultaneously
- **Risk Mitigation**: Problems in one component don't necessarily affect others
- **Progress Tracking**: Completion of components provides measurable progress
- **Expertise Matching**: Different components can be assigned to appropriate specialists
- **Testing and Validation**: Components can be verified independently before integration
-- SmartDesk — AlloyDB Schema Setup
-- Personal CRM dataset: contacts, notes, tasks
-- This is a CUSTOM dataset (not from any lab default)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant embedding function access
GRANT EXECUTE ON FUNCTION embedding TO postgres;

-- =============================================================================
-- Table: contacts
-- =============================================================================
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    phone VARCHAR(50),
    company VARCHAR(200),
    role VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- Table: notes (with vector embeddings for semantic search)
-- =============================================================================
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- Table: tasks
-- =============================================================================
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'done')),
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    due_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- Sample Data: Contacts
-- =============================================================================
INSERT INTO contacts (name, email, phone, company, role, notes) VALUES
('Priya Sharma', 'priya.sharma@techcorp.in', '+91-98765-43210', 'TechCorp India', 'Engineering Manager', 'Met at Google Cloud Summit. Interested in AI/ML partnerships.'),
('Arjun Mehta', 'arjun.m@startupx.io', '+91-87654-32109', 'StartupX', 'CTO', 'Building a SaaS product on GCP. Wants to explore AlloyDB.'),
('Sneha Reddy', 'sneha.reddy@designhub.com', '+91-76543-21098', 'DesignHub', 'Product Designer', 'Collaborating on the new dashboard UI. Prefers async communication.'),
('Rahul Gupta', 'rahul.g@cloudops.dev', '+91-65432-10987', 'CloudOps', 'DevOps Lead', 'Handles our CI/CD pipeline. Key contact for deployment issues.'),
('Ananya Das', 'ananya.das@university.edu', '+91-54321-09876', 'IIT Research Lab', 'Research Associate', 'Working on NLP research. Potential intern hire for Q3.');

-- =============================================================================
-- Sample Data: Notes (embeddings generated on insert)
-- =============================================================================
INSERT INTO notes (title, content, content_embedding) VALUES
('Q3 Product Launch Planning', 'Discussed the Q3 product launch timeline with Priya and Arjun. Key milestones: MVP by July 15, beta by Aug 1, GA by Sept 10. Need to finalize the pricing model and prepare marketing collateral. Arjun suggested using AlloyDB for the analytics backend.', embedding('text-embedding-005', 'Discussed the Q3 product launch timeline with Priya and Arjun. Key milestones: MVP by July 15, beta by Aug 1, GA by Sept 10. Need to finalize the pricing model and prepare marketing collateral. Arjun suggested using AlloyDB for the analytics backend.')::vector),

('Weekly Standup Notes - March 28', 'Team standup highlights: Frontend is on track for the dashboard redesign. Sneha presented new wireframes. Backend API migration to Cloud Run is 80% complete. Rahul flagged a potential issue with the staging environment SSL certs. Action item: Rahul to fix SSL by Monday.', embedding('text-embedding-005', 'Team standup highlights: Frontend is on track for the dashboard redesign. Sneha presented new wireframes. Backend API migration to Cloud Run is 80% complete. Rahul flagged a potential issue with the staging environment SSL certs. Action item: Rahul to fix SSL by Monday.')::vector),

('AI Agent Architecture Discussion', 'Met with the team to discuss the multi-agent architecture for SmartDesk. Decided on ADK with Gemini as the orchestrator. Sub-agents will handle email, calendar, and knowledge base queries. MCP integration for Gmail and Calendar. AlloyDB with vector search for the notes database. Deployment target: Cloud Run.', embedding('text-embedding-005', 'Met with the team to discuss the multi-agent architecture for SmartDesk. Decided on ADK with Gemini as the orchestrator. Sub-agents will handle email, calendar, and knowledge base queries. MCP integration for Gmail and Calendar. AlloyDB with vector search for the notes database. Deployment target: Cloud Run.')::vector),

('Client Feedback Summary - TechCorp', 'Priya shared feedback from TechCorp stakeholders. They want faster query response times on the analytics dashboard. Current P95 latency is 2.3s, target is under 500ms. Suggested migrating from standard Postgres to AlloyDB for the columnar engine. Also requested a natural language query feature for non-technical users.', embedding('text-embedding-005', 'Priya shared feedback from TechCorp stakeholders. They want faster query response times on the analytics dashboard. Current P95 latency is 2.3s, target is under 500ms. Suggested migrating from standard Postgres to AlloyDB for the columnar engine. Also requested a natural language query feature for non-technical users.')::vector),

('Intern Interview Notes - Ananya Das', 'Interviewed Ananya from IIT Research Lab for the NLP intern position. Strong background in transformer models and embeddings. Published a paper on retrieval-augmented generation. Good fit for the vector search feature work. Recommendation: extend offer for Q3 internship starting July 1.', embedding('text-embedding-005', 'Interviewed Ananya from IIT Research Lab for the NLP intern position. Strong background in transformer models and embeddings. Published a paper on retrieval-augmented generation. Good fit for the vector search feature work. Recommendation: extend offer for Q3 internship starting July 1.')::vector);

-- =============================================================================
-- Sample Data: Tasks
-- =============================================================================
INSERT INTO tasks (title, description, status, priority, due_date) VALUES
('Finalize Q3 pricing model', 'Work with Arjun to finalize the SaaS pricing tiers before the product launch.', 'pending', 'high', '2026-04-15'),
('Review Sneha wireframes', 'Go through the new dashboard wireframes and provide feedback.', 'in_progress', 'medium', '2026-04-05'),
('Fix staging SSL certs', 'Rahul to resolve the SSL certificate issue on staging environment.', 'pending', 'high', '2026-04-03'),
('Prepare hackathon demo', 'Build and test the SmartDesk multi-agent demo for the Google Cloud hackathon.', 'in_progress', 'high', '2026-04-10'),
('Send intern offer to Ananya', 'Draft and send the internship offer letter for the Q3 NLP intern position.', 'pending', 'medium', '2026-04-08'),
('Migrate analytics to AlloyDB', 'Plan and execute the migration of the analytics backend from standard Postgres to AlloyDB.', 'pending', 'medium', '2026-04-20'),
('Write API documentation', 'Document all SmartDesk API endpoints for the Cloud Run deployment.', 'pending', 'low', '2026-04-25');

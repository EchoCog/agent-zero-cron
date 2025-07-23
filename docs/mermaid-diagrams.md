# Mermaid Diagrams in Agent Zero Architecture

## Overview
This document explains the Mermaid diagrams that have been added to the Agent Zero architecture documentation to provide visual representations of the system's components and their relationships.

## Diagrams Added

### 1. System Architecture Overview (`graph TB`)
- **Purpose**: Shows the hierarchical relationship between agents and shared resources
- **Key Elements**: 
  - Agent hierarchy (User/Agent 0 → Sub-agents)
  - Shared assets (Prompts, Memory, Knowledge, Extensions, Instruments)
  - Tool ecosystem accessible to all agents

### 2. Runtime Architecture (`flowchart TB`)
- **Purpose**: Illustrates the Docker-based runtime environment
- **Key Elements**:
  - Host system components (Browser, Docker Engine)
  - Container layers (Web Layer, Core Engine, Storage, Runtime)
  - External service integrations

### 3. Interaction Flow (`sequenceDiagram`)
- **Purpose**: Details the step-by-step interaction flow between components
- **Key Elements**:
  - User input processing
  - VectorDB initialization and memory access
  - Tool execution and LLM interaction
  - Sub-agent delegation patterns

### 4. Component Relationships (`graph TB`)
- **Purpose**: Comprehensive overview of all major framework components
- **Key Elements**:
  - Six main layers: Agent, Core Systems, Extensibility, Data, Runtime, External
  - Inter-component connections and data flow

### 5. Tools Architecture (`graph TB`)
- **Purpose**: Detailed view of the tool system organization
- **Key Elements**:
  - Tool categorization (Core, Execution, Data, Memory, Scheduling)
  - External data source integrations
  - Tool executor relationships

### 6. Memory System Architecture (`flowchart TB`)
- **Purpose**: Complete memory system workflow and components
- **Key Elements**:
  - Input sources and memory types
  - Processing layer with VectorDB
  - Message management and compression
  - Storage backend architecture

### 7. Prompt System Architecture (`flowchart TB`)
- **Purpose**: Prompt organization and dynamic behavior system
- **Key Elements**:
  - Core and tool prompts hierarchy
  - Custom prompt organization
  - Dynamic behavior adjustment workflow

### 8. Extensions System Architecture (`flowchart TB`)
- **Purpose**: Extension system structure and execution flow
- **Key Elements**:
  - Extension categories and types
  - Execution order and naming conventions
  - Custom extension development process

## Benefits of Mermaid Diagrams

1. **Maintainability**: Text-based diagrams are easier to version control and update
2. **Consistency**: Standardized styling and layout across all diagrams
3. **Readability**: Clean, professional appearance with consistent color coding
4. **Accessibility**: Diagrams render properly in GitHub, documentation sites, and IDEs
5. **Collaboration**: Easy for contributors to modify and extend diagrams

## Color Coding Scheme

- **Blue tones**: Core agent and system components
- **Orange tones**: Execution and tool components  
- **Green tones**: Data and knowledge components
- **Purple tones**: Memory and storage components
- **Pink tones**: Runtime and infrastructure components
- **Light green tones**: External services and interfaces

## Viewing the Diagrams

These Mermaid diagrams will render automatically in:
- GitHub repository views
- Documentation websites that support Mermaid
- VS Code with Mermaid extensions
- Many other Markdown viewers and editors

The diagrams complement the existing SVG diagrams and provide a more maintainable, text-based approach to architectural documentation.
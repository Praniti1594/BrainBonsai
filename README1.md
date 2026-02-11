
# BrainBonsai 🌳🧠

AI-Powered Web3 Learning Tree with Blockchain Simulation & Automatic NFT Rewards

BrainBonsai is an interactive Web3 education platform that combines AI-generated knowledge trees, blockchain simulation, structured progression, and automatic NFT minting into a gamified learning experience.

Users grow structured learning trees, unlock knowledge step-by-step, understand blockchain by simulating it, and earn NFTs automatically as proof of mastery.

---

## 🌱 Project Overview

BrainBonsai transforms complex blockchain and smart contract concepts into a visual tree-based journey.

Users:

* Log in using Google authentication
* Automatically receive a blockchain wallet (no MetaMask required)
* Choose a seed topic (e.g., Smart Contracts)
* Grow AI-generated structured subtopics
* Unlock deeper knowledge through lock-based progression
* Automatically mint NFTs when mastery milestones are reached
* Learn blockchain mechanics through an interactive simulator

The tree visually represents knowledge growth. Branches expand into structured subtopics generated using Groq AI.

---

## 🚀 Core Features

### 🌳 AI-Generated Knowledge Trees (Groq AI)

Users select a seed topic such as:

* Smart Contracts
* Blockchain Fundamentals
* NFTs
* DeFi

Groq AI generates structured subtopics dynamically, forming branches that expand logically from the root.

The system maintains topic hierarchy and ensures meaningful progression.

---

### 🔐 Lock-Based Learning System

BrainBonsai enforces structured mastery:

* Users cannot unlock deeper branches unless prerequisite branches are completed
* Prevents skipping foundational knowledge
* Encourages sequential understanding

This ensures conceptual clarity instead of surface-level browsing.

---

### 🪙 Automatic NFT Minting

NFT rewards are generated automatically.

When:

* A knowledge tree grows beyond 8 branches
* The user completes structured progression milestones

An NFT is minted automatically via Solidity smart contracts.

The NFT represents proof of learning achievement and is sent directly to the user's generated wallet.

No manual minting required.

---

### 🔐 Google Authentication + Wallet Creation

To remove Web3 friction:

* Users log in using Google OAuth
* A blockchain wallet is automatically generated
* No MetaMask setup required
* Designed for beginners entering Web3

Wallets are securely tied to user accounts and interact with the smart contract system for NFT minting.

---

## 🌿 BlockLearn — Interactive Blockchain Simulator

BrainBonsai includes a fully interactive blockchain simulator called **BlockLearn**.

Instead of reading about blockchain concepts, users simulate them directly.

### What Users Learn:

* Wallet creation
* Public & private keys
* Blockchain ledger mechanics
* Transactions
* Gas fees
* Mempool behavior
* Block mining
* Hashing
* Transaction confirmation

---

### 🪙 Bonsai Token (BON)

The simulator uses **Bonsai Token (BON)**:

* BON behaves like ETH
* Used for sending transactions
* Demonstrates gas mechanics safely
* No real crypto involved

---

### 🔁 Transaction Lifecycle Simulation

Users can:

1. Create a wallet
2. Generate an address
3. Send BON tokens
4. Select gas speed (Slow / Standard / Fast)
5. Sign and broadcast transactions
6. Watch transactions move:

   * Wallet → Mempool → Block
7. View the public blockchain ledger
8. Inspect blocks, hashes, gas fees, and transaction amounts

The journey overlay visually shows how transactions propagate through the network.

This interactive simulation teaches blockchain fundamentals intuitively.

---

## 🧠 Game Flow

### Step 1: Login

Google authentication creates a wallet automatically.

### Step 2: Choose a Seed

Select a topic like Smart Contracts.

### Step 3: Grow the Tree

Groq AI generates structured subtopics as branches.

### Step 4: Unlock Knowledge

Complete branches to unlock deeper concepts.

### Step 5: Reach Milestone

When tree size exceeds 8+ branches, NFT minting triggers automatically.

### Step 6: Learn Blockchain

Use BlockLearn simulator to understand real blockchain mechanics interactively.

---

## 🧱 Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* SQLite
* Google OAuth
* Groq AI API

### Frontend

* Vanilla JavaScript
* HTML5 Canvas
* Interactive simulation modules

### Blockchain

* Solidity smart contracts
* Automated NFT minting logic
* Wallet generation system

---

## 🔗 Smart Contracts

Written in Solidity.

Responsibilities:

* Mint achievement NFTs
* Store metadata for learning milestones
* Interact with backend wallet system
* Trigger minting automatically when tree milestone conditions are met

---

## 🗄 Database Design

Core entities:

* User
* Wallet
* LearningSession
* Branch
* NFTAchievement
* BlockchainSimulationState

Learning state is stored to enforce progression locks and milestone tracking.

---

## ⚙️ Installation & Setup

### Prerequisites

* Python 3.8+
* Virtual environment recommended

---

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Server runs at:

```
http://localhost:8001
```

---

### Environment Variables

Create a `.env` file in `backend/`:

```
GROQ_API_KEY=your_groq_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
BLOCKCHAIN_PRIVATE_KEY=your_private_key
```

---

## 🎯 Vision

BrainBonsai aims to:

* Remove Web3 onboarding friction
* Teach blockchain mechanics interactively
* Enforce structured mastery
* Reward learning with verifiable NFTs
* Combine AI + Education + Blockchain into one ecosystem

It is a beginner-friendly Web3 learning platform where knowledge grows like a tree — and mastery becomes a digital asset.


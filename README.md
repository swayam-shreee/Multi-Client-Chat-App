# Multi-Client Chat Application with AWS Deployment

**Date:** October 2025

A distributed chat system built with Python sockets that demonstrates real-time communication and scalability. The application is deployed on AWS, leveraging Elastic Load Balancing (ELB), EC2, ElastiCache (Redis), and CloudWatch for robust performance and monitoring. 

![AWS Architecture Diagram](ChatAppAWS_Architecture.png)

## Key Features

* **Real-Time TCP Server:** Utilizes Python’s `socket` library and `threading` to concurrently manage multiple client connections and broadcast messages.
* **Cloud Deployment:** Hosted on AWS EC2, allowing clients from different networks to connect globally via a public IP or DNS.
* **Horizontal Scalability:** Employs an AWS Elastic Load Balancer to seamlessly distribute incoming chat traffic across multiple EC2 server instances.
* **Cross-Instance Synchronization:** Integrates AWS ElastiCache (Redis) using a Pub/Sub model to ensure messages are instantly synchronized across all server nodes.
* **System Monitoring:** Uses AWS CloudWatch to track instance health, load balancer traffic, and overall system performance.

## Technologies Used

* **Language:** Python 3.12.5
* **Core Libraries:** `socket`, `threading`, `redis`, `os`
* **Infrastructure:** AWS EC2, AWS Elastic Load Balancing (ELB), AWS ElastiCache (Serverless Redis), AWS CloudWatch

---

## Architecture Overview

1. **Clients** run `client_aws.py` and initiate a connection to the Load Balancer's DNS.
2. **AWS ELB** routes the incoming TCP connection to one of the active **EC2 Instances** running `server_aws.py`.
3. When a client sends a message, the receiving EC2 instance immediately publishes it to **AWS ElastiCache (Redis)** via the `chatroom` channel.
4. All active EC2 instances are actively subscribed to the Redis `chatroom` channel.
5. Upon receiving the published message from Redis, each EC2 instance broadcasts the text to its directly connected local clients.

---

## Setup and Installation

### Prerequisites

* An active AWS Account.
* Python 3.12.5 installed on your local testing machine and AWS EC2 instances.
* The `redis` Python package installed on your servers (`pip install redis`).

### AWS Configuration Steps

1. Provision an **ElastiCache Serverless Redis** cache in your preferred AWS region.
2. Launch one or more **EC2 instances** in the same VPC and ensure security groups allow inbound traffic on port `12345` and outbound traffic to the Redis port `6379`.
3. Create a **Network Load Balancer** forwarding TCP traffic on port `12345` to your EC2 Target Group.
4. Update the `REDIS_ENDPOINT` variable at the bottom of `server_aws.py` with your specific ElastiCache configuration endpoint.

### Running the Server

Execute the following command on your configured EC2 instances:

```bash
python3 server_aws.py

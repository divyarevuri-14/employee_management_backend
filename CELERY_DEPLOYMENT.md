# Celery Beat and Monitoring – Deployment Topology

## 1. Components

- **Django Application:** Handles API requests and business logic.
- **Redis:** Acts as the Celery message broker and stores queued tasks.
- **Celery Worker:** Picks up tasks from Redis and executes them in the background.
- **Celery Beat:** Schedules periodic tasks, such as daily employee reports and inactive-employee maintenance.
- **PostgreSQL:** Stores employee and application data.
- **Logs:** Record task start, completion, duration, and failure details.

## 2. Task Execution Flow

1. Celery Beat checks the configured schedule.
2. When a task is due, Beat sends the task message to Redis.
3. Celery Worker receives the task from Redis.
4. The worker executes the task and interacts with PostgreSQL if required.
5. Task logs record the execution result and duration.

## 3. Deployment Notes

- Django, Redis, Celery Worker, and Celery Beat must be configured with compatible settings.
- Redis must be running and reachable by the worker and Beat.
- Celery Beat should run as a single scheduler instance for the same schedule.
- In production, run the worker and Beat as separate managed processes.
- Monitor worker availability, task failures, and queue depth.
- Configure persistent logging and appropriate log rotation for production.

## 4. Health Checks

- Verify Redis connectivity.
- Verify that the Celery worker is online.
- Verify that Celery Beat publishes scheduled tasks.
- Check task success and failure logs.
- Check the number of pending tasks in Redis.
- Confirm that scheduled tasks execute at the expected time.
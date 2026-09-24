# Query Optimization

## Objective

Identify and optimize N+1 database queries in the Employee API.

## N+1 Query Problem

Initially, the Employee queryset was:

```python
employees = Employee.objects.all()
```

Inside the loop, related objects were accessed:

* `employee.department_fk`
* `employee.profile`
* `employee.projects.all()`

This caused additional database queries for each employee and resulted in an N+1 query problem.

## Before Optimization

The initial query count was measured using Django's `connection.queries`.

**Total Queries: 94**

## Optimization Applied

The queryset was optimized using `select_related()` and `prefetch_related()`:

```python
employees = Employee.objects.select_related(
    "department_fk",
    "profile"
).prefetch_related(
    "projects"
)
```

### select_related()

`select_related()` was used for:

* `department_fk` — ForeignKey
* `profile` — OneToOne relationship

These related records are retrieved using SQL JOINs.

### prefetch_related()

`prefetch_related()` was used for:

* `projects` — ManyToMany relationship

The related projects are fetched separately and efficiently combined by Django.

## After Optimization

After applying the optimized queryset:

**Optimized Queries: 2**

## Performance Comparison

| Metric           | Before Optimization | After Optimization |
| ---------------- | ------------------: | -----------------: |
| Database Queries |                  94 |                  2 |

The number of database queries was reduced by **92 queries**, approximately **97.9% fewer queries**.

## Optimized API

The optimized queryset is used in:

```text
GET /api/v1/employees/details/
```

## Conclusion

The N+1 query problem was identified and resolved using Django ORM optimization techniques.

`select_related()` was used for ForeignKey and OneToOne relationships, while `prefetch_related()` was used for the ManyToMany relationship.

The query count was reduced from 94 to 2, significantly reducing unnecessary database round trips.

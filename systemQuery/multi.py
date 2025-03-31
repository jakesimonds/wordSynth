import multiprocessing

# Number of physical cores
physical_cores = multiprocessing.cpu_count() // 2

# Number of logical cores (with hyperthreading)
logical_cores = multiprocessing.cpu_count()

print(f"Physical cores: {physical_cores}")
print(f"Logical cores: {logical_cores}")
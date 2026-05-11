import sys
print("Python:", sys.executable)
try:
    import datasets
    print("datasets OK:", datasets.__version__)
except ImportError as e:
    print("datasets MISSING:", e)
try:
    import transformers
    print("transformers OK:", transformers.__version__)
except ImportError as e:
    print("transformers MISSING:", e)
try:
    import sklearn
    print("sklearn OK:", sklearn.__version__)
except ImportError as e:
    print("sklearn MISSING:", e)
try:
    import accelerate
    print("accelerate OK:", accelerate.__version__)
except ImportError as e:
    print("accelerate MISSING:", e)

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()

import numpy as np
import os
import pickle
import tarfile
from datetime import timezone
from djangoratings.models import Vote
from main.models import Resource, User
from spotlight.cross_validation import user_based_train_test_split
from spotlight.interactions import Interactions
from spotlight.sequence.implicit import ImplicitSequenceModel
from spotlight.sequence.representations import PoolNet
import torch

from base.settings import MEDIA_ROOT

def train_new_model():
        '''
        Trains and saves a Spotlight model
        '''
        os.environ['Training_Model'] = True
        timestamps0 = []
        user_ids = []
        item_ids = []
        max_resource_pk = 0
        for resource in Resource.objects.all():
                if resource.pk > max_resource_pk:
                        max_resource_pk = resource.pk
        max_user_pk = 0
        for user in User.objects.all():
                if user.pk > max_user_pk:
                        max_user_pk = user.pk
        num_users = max_user_pk + 1 # To make spotlight happy, not sure why this is necessary
        for vote in Vote.objects.all():
                if vote.score > 3:
                        timestamps0.append(vote.date_changed)
                        user_ids.append(vote.user.id)
                        item_ids.append(vote.object_id)

        timestamps1 = []
        for dt in timestamps0:
                timestamps1.append(dt.replace(tzinfo=timezone.utc).timestamp())

        user_ids = np.array(user_ids, dtype=np.int32)
        item_ids = np.array(item_ids, dtype=np.int32)
        timestamps = np.array(timestamps1, dtype=np.int32)

        interactions = Interactions(user_ids, 
                                    item_ids, 
                                    timestamps=timestamps, 
                                    num_users=num_users,
                                    num_items=max_resource_pk)

        net = PoolNet(max_resource_pk)

        model = ImplicitSequenceModel(net, use_cuda=torch.cuda.is_available())

        model.fit(interactions)

        with open(os.path.join(MEDIA_ROOT, 'model'), 'wb') as f:
                torch.save(model, f)

        os.environ['Training_Model'] = False
        return True

# The actual file ends here, the below is used for local model testing

# import torch

# from spotlight.evaluation import sequence_mrr_score
# from spotlight.sequence.implicit import ImplicitSequenceModel
# from spotlight.sequence.representations import LSTMNet

# train_interactions = train_data[0]
# num_resources = train_data[1]

# net = LSTMNet(num_resources) 

# model = ImplicitSequenceModel(representation=net, #Adjust hyperparameters here
#                                 use_cuda=torch.cuda.is_available()) 

# model.fit(train_interactions)

# sequence = np.array([1,2,4])
# matching_resources = np.array([4,5,7,100])

# predictions = model.predict(sequence)#, item_ids=matching_resources)

# print(predictions)

# from base.settings import SAGEMAKER_ENDPOINT_NAME
# import json
# from sagemaker.predictor import RealTimePredictor

# user_sequence = [4]
# resource_pks = [1,2,3]
# input = [user_sequence, resource_pks] # data=sequence of user interactions, resource_pks=ids of potential recommendations
# serialized_input = json.dumps(input)
# predictor = RealTimePredictor(SAGEMAKER_ENDPOINT_NAME, content_type='application/json') #resource_pks is currently ignored in SageMaker, so scores are given for all resources
# json_scores = predictor.predict(serialized_input)
# scores = json.loads(json_scores)
# score_array = np.array(scores)
# np_recommendation_pks = np.argsort(-score_array)
# recommendation_pks = list(np_recommendation_pks)
# print(recommendation_pks)
from models import Observation


def extract_resource_data(observation):
    """
    Extract the resource data from the observation.

    :param observation: The observation to extract the resource data from.
    :type observation: Observation
    :return: The resource data.
    :rtype: dict
    """
    # TODO: extract data from observation message not only from observation details
    resource_data = {
        'authors': observation.authors,  # list of authors in string format
        'publication_date': observation.details['content_trust.publication_date'],  # utcnow().timestamp() float
        'related_resources': observation.details['content_trust.related_resources'],  # list of related resources
        'topics': observation.details['content_trust.topics'],  # list of topics in string
    }
    return resource_data

import pytest
from fastapi import status

from tests.helpers import show_status_and_response
from tests.test_data import scheduler

test_job_ids = [job.id for job in scheduler.BASE_DATA]


def test_index(insert_jobs_in_test_scheduler, test_app):
    response = test_app.get('/scheduler/')
    assert response.status_code == status.HTTP_200_OK, show_status_and_response(response)
    assert b'<title>Scheduler</title>' in response.data


@pytest.mark.parametrize('job_id', test_job_ids)
def test_pause_and_resume_job(insert_jobs_in_test_scheduler, test_app, test_jobstore, job_id):
    resume_response = test_app.post('/scheduler/', data={'job_id': job_id, 'action': 'pause_job'})
    assert resume_response.status_code == status.HTTP_200_OK, show_status_and_response(resume_response)
    assert test_jobstore.lookup_job(job_id).next_run_time is None

    resume_response = test_app.post('/scheduler/', data={'job_id': job_id, 'action': 'resume_job'})
    assert resume_response.status_code == status.HTTP_200_OK, show_status_and_response(resume_response)
    assert test_jobstore.lookup_job(job_id).next_run_time is not None


@pytest.mark.parametrize('job_id', test_job_ids)
def test_delete_job(insert_jobs_in_test_scheduler, test_app, test_jobstore, job_id):
    response = test_app.post('/scheduler/', data={'job_id': job_id, 'action': 'delete_job'})
    assert response.status_code == status.HTTP_200_OK, show_status_and_response(response)
    assert test_jobstore.lookup_job(job_id) is None
import { Resource } from 'kolibri.lib.apiResource';

/**
 * @example Get a Collection of Assessments Groups for a given class
 * AssessmentResource.fetchCollection({ getParams: { collection: classId } })
 */
export default new Resource({
    name: 'assessmentgroup',
    idKey: 'id',
});
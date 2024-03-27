import { Resource } from 'kolibri.lib.apiResource';

/**
 * @example Get a Collection of Assessments for a given class
 * AssessmentResource.fetchCollection({ getParams: { collection: classId } })
 */
export default new Resource({
    name: 'assessment',
    idKey: 'id',
    fetchQuizzesSizes(getParams = {}) {
      return this.fetchListCollection('size', getParams);
    },
});
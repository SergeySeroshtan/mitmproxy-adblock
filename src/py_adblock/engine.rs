use adblock::request::Request as AdblockRequest;
use adblock::Engine as AdblockEngine;
use pyo3::prelude::*;

use crate::py_adblock::BlockerResult as AdblockBlockerResult;
use crate::py_adblock::FilterSet as AdblockFilterSet;

#[pyclass(unsendable)]
pub struct Engine {
    engine: AdblockEngine,
}

#[pymethods]
impl Engine {
    #[new]
    fn new() -> Self {
        let engine = AdblockEngine::default();
        Self { engine }
    }

    #[staticmethod]
    pub fn from_filter_set(set: &AdblockFilterSet, optimize: bool) -> Self {
        let engine = AdblockEngine::from_filter_set(set.filter_set.clone(), optimize);
        Self { engine }
    }

    #[pyo3(signature = (url, source_url, request_resource_type = "other"))]
    pub fn check_network_request(
        &self,
        url: &str,
        source_url: &str,
        request_resource_type: &str,
    ) -> PyResult<AdblockBlockerResult> {
        let request = AdblockRequest::new(url, source_url, request_resource_type);
        if let Err(e) = request {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Invalid request: {}",
                e
            )));
        }
        let request = request.unwrap();
        let result = self.engine.check_network_request(&request);

        Ok(AdblockBlockerResult::from(result))
    }
}

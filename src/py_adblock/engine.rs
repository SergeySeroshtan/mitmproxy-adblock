use adblock::Engine as AdblockEngine;
use pyo3::prelude::*;

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

    fn check(&self, request: &str) -> PyResult<bool> {
        // Here you would implement the logic to check the request against the adblock rules.
        // For now, we just return true for demonstration purposes.
        println!("Checking request: {:?}", request);
        Ok(true)
    }
}

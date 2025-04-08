use adblock::Engine as AdblockEngine;
use pyo3::prelude::*;

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

    fn check(&self, request: &str) -> PyResult<bool> {
        // Here you would implement the logic to check the request against the adblock rules.
        // For now, we just return true for demonstration purposes.
        println!("Checking request: {:?}", request);
        Ok(true)
    }
}

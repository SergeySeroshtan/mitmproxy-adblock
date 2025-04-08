use adblock::{lists::ParseOptions, FilterSet as AdblockFilterSet};
use pyo3::prelude::*;

#[pyclass]
pub struct FilterSet {
    pub(crate) filter_set: AdblockFilterSet,
}

#[pymethods]
impl FilterSet {
    #[new]
    fn new() -> Self {
        let filter_set = AdblockFilterSet::default();
        Self { filter_set }
    }

    fn add_filter_list(&mut self, filter_list: &str) -> PyResult<()> {
        self.filter_set
            .add_filter_list(filter_list, ParseOptions::default());
        Ok(())
    }
}

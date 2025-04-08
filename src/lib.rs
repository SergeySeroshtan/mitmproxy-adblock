mod py_adblock;
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn mitmproxy_adblock(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<py_adblock::Engine>()?;
    m.add_class::<py_adblock::FilterSet>()?;
    Ok(())
}

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControl,
  FormControlLabel,
  FormHelperText,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  TextField,
  Typography,
  Alert,
  Autocomplete,
  Chip,
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import serverService, {
  Server,
  ServerTag,
  CreateServerData,
  UpdateServerData,
  TestConnectionData,
  TestConnectionResult,
} from '../../services/serverService';

interface ServerFormProps {
  serverId?: number;
  initialData?: Server;
}

const ServerForm: React.FC<ServerFormProps> = ({ serverId, initialData }) => {
  const navigate = useNavigate();
  const isEditMode = Boolean(serverId);

  // Form state
  const [formData, setFormData] = useState<CreateServerData | UpdateServerData>({
    name: '',
    ip_address: '',
    ssh_port: 22,
    description: '',
    is_active: true,
    credentials: {
      username: '',
      auth_type: 'password',
      password: '',
      private_key: '',
    },
    tags: [],
  });

  // UI state
  const [loading, setLoading] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [testing, setTesting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<TestConnectionResult | null>(null);
  const [availableTags, setAvailableTags] = useState<ServerTag[]>([]);
  const [selectedTags, setSelectedTags] = useState<ServerTag[]>([]);

  // Form validation
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Load initial data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch available tags
        const tags = await serverService.getTags();
        setAvailableTags(tags);

        // If in edit mode and no initialData provided, fetch server data
        if (isEditMode && serverId && !initialData) {
          const serverData = await serverService.getServer(serverId);
          setFormData({
            name: serverData.name,
            ip_address: serverData.ip_address,
            ssh_port: serverData.ssh_port,
            description: serverData.description || '',
            is_active: serverData.is_active,
            credentials: {
              username: serverData.credentials.username,
              auth_type: serverData.credentials.auth_type,
              // Password and private key are not returned from the API for security
              password: '',
              private_key: '',
            },
            tags: serverData.tags.map(tag => tag.name),
          });
          setSelectedTags(serverData.tags);
        } else if (initialData) {
          // Use provided initialData
          setFormData({
            name: initialData.name,
            ip_address: initialData.ip_address,
            ssh_port: initialData.ssh_port,
            description: initialData.description || '',
            is_active: initialData.is_active,
            credentials: {
              username: initialData.credentials.username,
              auth_type: initialData.credentials.auth_type,
              // Password and private key are not returned from the API for security
              password: '',
              private_key: '',
            },
            tags: initialData.tags.map(tag => tag.name),
          });
          setSelectedTags(initialData.tags);
        }
      } catch (err) {
        console.error('Error loading form data:', err);
        setError('Failed to load form data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [serverId, initialData, isEditMode]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name) newErrors.name = 'Name is required';
    if (!formData.ip_address) newErrors.ip_address = 'IP address is required';
    if (!formData.ssh_port) newErrors.ssh_port = 'SSH port is required';
    if (formData.ssh_port && (formData.ssh_port < 1 || formData.ssh_port > 65535)) {
      newErrors.ssh_port = 'SSH port must be between 1 and 65535';
    }

    if (!formData.credentials?.username) {
      newErrors['credentials.username'] = 'Username is required';
    }

    if (formData.credentials?.auth_type === 'password' && !formData.credentials?.password && !isEditMode) {
      newErrors['credentials.password'] = 'Password is required';
    }

    if (formData.credentials?.auth_type === 'key' && !formData.credentials?.private_key && !isEditMode) {
      newErrors['credentials.private_key'] = 'Private key is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    if (name.startsWith('credentials.')) {
      const credentialField = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        credentials: {
          ...prev.credentials,
          [credentialField]: value,
        },
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSwitchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };

  const handleSelectChange = (e: any) => {
    const { name, value } = e.target;
    
    if (name.startsWith('credentials.')) {
      const credentialField = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        credentials: {
          ...prev.credentials,
          [credentialField]: value,
        },
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleTagsChange = (_event: React.SyntheticEvent, value: ServerTag[]) => {
    setSelectedTags(value);
    setFormData(prev => ({
      ...prev,
      tags: value.map(tag => tag.name),
    }));
  };

  const handleTestConnection = async () => {
    if (!validateForm()) return;

    setTesting(true);
    setTestResult(null);
    setError(null);

    try {
      const testData: TestConnectionData = {
        ip_address: formData.ip_address as string,
        ssh_port: formData.ssh_port as number,
        username: formData.credentials?.username as string,
        auth_type: formData.credentials?.auth_type as 'password' | 'key',
        password: formData.credentials?.password,
        private_key: formData.credentials?.private_key,
      };

      const result = await serverService.testConnection(testData);
      setTestResult(result);
    } catch (err) {
      console.error('Error testing connection:', err);
      setError('Failed to test connection. Please check your inputs and try again.');
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSaving(true);
    setError(null);

    try {
      if (isEditMode && serverId) {
        // Update existing server
        await serverService.updateServer(serverId, formData as UpdateServerData);
      } else {
        // Create new server
        await serverService.createServer(formData as CreateServerData);
      }
      navigate('/servers');
    } catch (err) {
      console.error('Error saving server:', err);
      setError('Failed to save server. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h1">
          {isEditMode ? 'Edit Server' : 'Add New Server'}
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            type="button"
            variant="outlined"
            startIcon={<CancelIcon />}
            onClick={() => navigate('/servers')}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            disabled={saving}
          >
            {isEditMode ? 'Update Server' : 'Add Server'}
          </Button>
        </Stack>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {testResult && (
        <Alert 
          severity={testResult.success ? 'success' : 'error'} 
          sx={{ mb: 3 }}
          icon={testResult.success ? <CheckIcon /> : undefined}
        >
          {testResult.message}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Server Information
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Stack spacing={3}>
                <TextField
                  label="Server Name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  fullWidth
                  required
                  error={!!errors.name}
                  helperText={errors.name}
                />

                <TextField
                  label="IP Address"
                  name="ip_address"
                  value={formData.ip_address}
                  onChange={handleInputChange}
                  fullWidth
                  required
                  error={!!errors.ip_address}
                  helperText={errors.ip_address}
                />

                <TextField
                  label="SSH Port"
                  name="ssh_port"
                  type="number"
                  value={formData.ssh_port}
                  onChange={handleInputChange}
                  fullWidth
                  required
                  inputProps={{ min: 1, max: 65535 }}
                  error={!!errors.ssh_port}
                  helperText={errors.ssh_port}
                />

                <TextField
                  label="Description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  fullWidth
                  multiline
                  rows={3}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_active as boolean}
                      onChange={handleSwitchChange}
                      name="is_active"
                      color="primary"
                    />
                  }
                  label="Active"
                />

                <Autocomplete
                  multiple
                  id="tags"
                  options={availableTags}
                  value={selectedTags}
                  onChange={handleTagsChange}
                  getOptionLabel={(option) => option.name}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        label={option.name}
                        {...getTagProps({ index })}
                        key={option.id}
                      />
                    ))
                  }
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Tags"
                      placeholder="Select tags"
                    />
                  )}
                />
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Connection Settings
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Stack spacing={3}>
                <TextField
                  label="Username"
                  name="credentials.username"
                  value={formData.credentials?.username}
                  onChange={handleInputChange}
                  fullWidth
                  required
                  error={!!errors['credentials.username']}
                  helperText={errors['credentials.username']}
                />

                <FormControl fullWidth>
                  <InputLabel id="auth-type-label">Authentication Type</InputLabel>
                  <Select
                    labelId="auth-type-label"
                    name="credentials.auth_type"
                    value={formData.credentials?.auth_type}
                    onChange={handleSelectChange}
                    label="Authentication Type"
                  >
                    <MenuItem value="password">Password</MenuItem>
                    <MenuItem value="key">SSH Key</MenuItem>
                  </Select>
                </FormControl>

                {formData.credentials?.auth_type === 'password' ? (
                  <TextField
                    label="Password"
                    name="credentials.password"
                    type="password"
                    value={formData.credentials?.password}
                    onChange={handleInputChange}
                    fullWidth
                    required={!isEditMode}
                    error={!!errors['credentials.password']}
                    helperText={
                      errors['credentials.password'] ||
                      (isEditMode ? 'Leave blank to keep current password' : '')
                    }
                  />
                ) : (
                  <TextField
                    label="Private Key"
                    name="credentials.private_key"
                    value={formData.credentials?.private_key}
                    onChange={handleInputChange}
                    fullWidth
                    multiline
                    rows={5}
                    required={!isEditMode}
                    error={!!errors['credentials.private_key']}
                    helperText={
                      errors['credentials.private_key'] ||
                      (isEditMode ? 'Leave blank to keep current key' : 'Paste your private key here')
                    }
                  />
                )}

                <Button
                  variant="outlined"
                  color="primary"
                  onClick={handleTestConnection}
                  disabled={testing}
                  startIcon={testing ? <CircularProgress size={20} /> : <CheckIcon />}
                  fullWidth
                >
                  Test Connection
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ServerForm;